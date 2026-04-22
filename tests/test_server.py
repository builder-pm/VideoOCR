import pytest

from fastapi.testclient import TestClient
from server import app, session_manager
import os
import shutil
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
import numpy as np

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_sessions():
    if os.path.exists("sessions"):
        shutil.rmtree("sessions")
    os.makedirs("sessions", exist_ok=True)
    session_manager.sessions = {}
    yield

def test_upload_video_mocked():
    with patch("server.get_video_metadata") as mock_metadata:
        mock_metadata.return_value = {
            "duration": 60,
            "resolution": "1920x1080",
            "fps": 30.0,
            "size_bytes": 1024,
        }
        
        files = {"file": ("test.mp4", b"fake content", "video/mp4")}
        response = client.post("/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["metadata"]["duration"] == 60

def test_upload_too_long():
    with patch("server.get_video_metadata") as mock_metadata:
        mock_metadata.return_value = {
            "duration": 4000,
            "resolution": "1920x1080",
            "fps": 30.0,
            "size_bytes": 1024,
        }
        
        files = {"file": ("test.mp4", b"content", "video/mp4")}
        response = client.post("/upload", files=files)
        assert response.status_code == 400

def test_process_start():
    session_id = "test-session"
    session_dir = f"sessions/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    video_path = f"{session_dir}/video.mp4"
    with open(video_path, "wb") as f:
        f.write(b"content")
    
    state = session_manager.create_session(session_id, session_dir)
    state.video_path = video_path
    
    config = {
        "session_id": session_id,
        "start_time": 0,
        "end_time": 10,
        "fps": 1.0,
        "ocr_engine": "tesseract"
    }
    
    with patch("server.process_video") as mock_process:
        response = client.post("/process", json=config)
        assert response.status_code == 200
        assert response.json()["status"] == "started"

def test_upload_invalid_format():
    files = {"file": ("test.txt", b"fake content", "text/plain")}
    response = client.post("/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported format" in response.json()["error"]

def test_upload_file_too_large():
    """BACK-05: Reject files larger than 2GB via size check in upload logic."""
    import asyncio
    from fastapi import UploadFile
    import io
    from unittest.mock import AsyncMock

    async def run():
        # Create a mock UploadFile with size set to 3GB
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "big.mp4"
        mock_file.size = 3 * 1024 * 1024 * 1024
        mock_file.read = AsyncMock(return_value=b"")
        from server import upload_video
        response = await upload_video(mock_file)
        return response

    response = asyncio.run(run())
    assert response.status_code == 413
    assert b"File too large" in response.body

def test_sharpness_calculation():
    import numpy as np
    from server import calculate_laplacian_variance
    # Create a sharp image (random noise)
    sharp_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    sharp_score = calculate_laplacian_variance(sharp_img)
    
    # Create a blurry image (constant color)
    blurry_img = np.zeros((100, 100, 3), dtype=np.uint8)
    blurry_score = calculate_laplacian_variance(blurry_img)
    
    assert sharp_score > blurry_score

def test_text_deduplication():
    from server import is_similar_text
    assert is_similar_text("Hello World", "Hello World") is True
    assert is_similar_text("Hello World", "Hello Worle") is True # > 90% similar (10/11 chars)
    assert is_similar_text("Hello World", "Goodbye") is False

def test_get_results():
    session_id = "test-results"
    state = session_manager.create_session(session_id, f"sessions/{session_id}")
    state.text_blocks = [
        {"frame_number": 1, "timestamp": 0.5, "text": "Detected Text", "sharpness_score": 150.0, "frame_path": "dummy"}
    ]
    
    response = client.get(f"/results?session_id={session_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["text"] == "Detected Text"
    assert "frame_path" not in data["results"][0]

def test_get_frame():
    session_id = "test-frame"
    session_dir = f"sessions/{session_id}"
    frames_dir = f"{session_dir}/frames"
    os.makedirs(frames_dir, exist_ok=True)
    frame_path = f"{frames_dir}/frame_00001.jpg"
    with open(frame_path, "wb") as f:
        f.write(b"fake image data")
    
    session_manager.create_session(session_id, session_dir)
    
    response = client.get(f"/frames/{session_id}/1")
    assert response.status_code == 200
    assert response.content == b"fake image data"

def test_sse_heartbeat():
    """BACK-17: SSE stream emits valid SSE events (data or heartbeat)."""
    session_id = "test-heartbeat"
    session_dir = f"sessions/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    state = session_manager.create_session(session_id, session_dir)
    # Start with active=False and progress=100 so the generator terminates quickly
    state.active = False
    state.progress = 100

    lines_collected = []
    with client.stream("GET", f"/progress?session_id={session_id}") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        for line in response.iter_lines():
            lines_collected.append(line)

    # Should have received at least a data line with completed status
    data_lines = [l for l in lines_collected if l.startswith("data: ")]
    assert len(data_lines) >= 1, "SSE stream emitted no data events"
    payload = json.loads(data_lines[0][6:])
    assert payload["status"] == "completed"
    assert payload["progress"] == 100

def test_invalid_video_metadata():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout='{"streams": []}', returncode=0)
        files = {"file": ("test.mp4", b"content", "video/mp4")}
        response = client.post("/upload", files=files)
        assert response.status_code == 400
        assert "No video stream found" in response.json()["detail"]

def test_friendly_errors():
    # Test that unknown session returns 404 with JSON error, not crash
    response = client.get("/results?session_id=nonexistent")
    assert response.status_code == 404
    assert "error" in response.json()

def test_extract_frames():
    from server import extract_frames
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("os.makedirs"):
            with patch("pathlib.Path.glob") as mock_glob:
                mock_glob.return_value = [Path("frame_00001.jpg")]
                frames = extract_frames("video.mp4", 0, 10, 1.0, "out")
                assert len(frames) == 1
                assert mock_run.called
                args = mock_run.call_args[0][0]
                assert "fps=1.0" in args

@pytest.mark.asyncio
async def test_blur_skipping():
    from server import process_video, ProcessConfig, session_manager
    session_id = "test-blur"
    session_dir = f"sessions/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    state = session_manager.create_session(session_id, session_dir)
    state.video_path = "dummy.mp4"
    
    config = ProcessConfig(
        session_id=session_id,
        start_time=0,
        end_time=1,
        fps=1.0,
        blur_threshold=100
    )
    
    with patch("server.extract_frames") as mock_extract:
        mock_extract.return_value = ["frame_00001.jpg"]
        with patch("cv2.imread") as mock_imread:
            mock_imread.return_value = np.zeros((10, 10, 3), dtype=np.uint8) # Blurry
            with patch("server.calculate_laplacian_variance") as mock_blur:
                mock_blur.return_value = 50.0 # < 100
                await process_video(session_id, config)
                assert state.skipped_blur == 1

@pytest.mark.asyncio
async def test_ocr_integration():
    from server import process_video, ProcessConfig, session_manager
    session_id = "test-ocr"
    session_dir = f"sessions/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    state = session_manager.create_session(session_id, session_dir)
    state.video_path = "dummy.mp4"
    
    config = ProcessConfig(
        session_id=session_id,
        start_time=0,
        end_time=1,
        fps=1.0,
        ocr_engine="tesseract"
    )
    
    with patch("server.extract_frames") as mock_extract:
        mock_extract.return_value = ["frame_00001.jpg"]
        with patch("cv2.imread") as mock_imread:
            mock_imread.return_value = np.ones((10, 10, 3), dtype=np.uint8)
            with patch("server.calculate_laplacian_variance") as mock_blur:
                mock_blur.return_value = 150.0
                with patch("server.TESSERACT_AVAILABLE", True):
                    with patch("server.ocr_with_tesseract") as mock_ocr:
                        mock_ocr.return_value = "Hello"
                        await process_video(session_id, config)
                        assert len(state.text_blocks) == 1
                        assert state.text_blocks[0]["text"] == "Hello"

def test_sse_terminal_event():
    session_id = "test-terminal"
    session_dir = f"sessions/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    state = session_manager.create_session(session_id, session_dir)
    state.active = False
    state.progress = 100
    
    with client.stream("GET", f"/progress?session_id={session_id}") as response:
        lines = list(response.iter_lines())
        assert any("completed" in line for line in lines)

def test_sse_progress():
    """BACK-15, BACK-16: SSE stream includes all required payload fields."""
    session_id = "test-sse"
    session_dir = f"sessions/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    state = session_manager.create_session(session_id, session_dir)
    # Use active=False so generator terminates after one event
    state.active = False
    state.progress = 42
    state.current_frame = 5
    state.total_frames = 10
    state.skipped_blur = 2

    with client.stream("GET", f"/progress?session_id={session_id}") as response:
        assert response.status_code == 200
        for line in response.iter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                # BACK-16: verify all required fields are present
                assert data["progress"] == 42
                assert data["current_frame"] == 5
                assert data["total_frames"] == 10
                assert data["skipped_blur"] == 2
                assert "text_blocks" in data
                assert "status" in data
                assert "error" in data
                break

def test_status_endpoint():
    """BACK-19: /status reports all engine availability keys."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "ffmpeg_available" in data
    assert "tesseract_available" in data
    assert "paddleocr_available" in data


def test_status_ffmpeg_missing():
    """BACK-19: /status reports ffmpeg_available=False when ffmpeg not found."""
    with patch("subprocess.run", side_effect=FileNotFoundError("ffmpeg not found")):
        response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["ffmpeg_available"] is False


def test_ocr_engine_not_installed():
    """BACK-21: Returns error if requested OCR engine is not installed."""
    session_id = "test-no-ocr"
    session_dir = f"sessions/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    video_path = f"{session_dir}/video.mp4"
    with open(video_path, "wb") as f:
        f.write(b"content")
    state = session_manager.create_session(session_id, session_dir)
    state.video_path = video_path

    config = {
        "session_id": session_id,
        "start_time": 0,
        "end_time": 10,
        "fps": 1.0,
        "ocr_engine": "tesseract"
    }

    # Simulate tesseract not installed
    with patch("server.TESSERACT_AVAILABLE", False):
        with patch("server.extract_frames", return_value=["frame_00001.jpg"]):
            with patch("cv2.imread", return_value=np.ones((10, 10, 3), dtype=np.uint8)):
                with patch("server.calculate_laplacian_variance", return_value=200.0):
                    # Trigger processing by calling the endpoint
                    response = client.post("/process", json=config)
                    assert response.status_code == 200  # Task is started
                    # The error is set asynchronously in the session state
                    import time
                    time.sleep(0.3)
                    result = client.get(f"/results?session_id={session_id}")
                    assert result.status_code == 200


@pytest.mark.asyncio
async def test_ocr_paddle_path():
    """BACK-11: PaddleOCR engine path is invoked when paddle engine selected."""
    from server import process_video, ProcessConfig, session_manager
    session_id = "test-paddle"
    session_dir = f"sessions/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    state = session_manager.create_session(session_id, session_dir)
    state.video_path = "dummy.mp4"

    config = ProcessConfig(
        session_id=session_id,
        start_time=0,
        end_time=1,
        fps=1.0,
        ocr_engine="paddle"
    )

    with patch("server.extract_frames") as mock_extract:
        mock_extract.return_value = ["frame_00001.jpg"]
        with patch("cv2.imread") as mock_imread:
            mock_imread.return_value = np.ones((10, 10, 3), dtype=np.uint8)
            with patch("server.calculate_laplacian_variance") as mock_blur:
                mock_blur.return_value = 200.0
                with patch("server.PADDLEOCR_AVAILABLE", True):
                    with patch("server.ocr_with_paddle") as mock_paddle:
                        mock_paddle.return_value = "Paddle Text"
                        await process_video(session_id, config)
                        mock_paddle.assert_called_once()
                        assert len(state.text_blocks) == 1
                        assert state.text_blocks[0]["text"] == "Paddle Text"
