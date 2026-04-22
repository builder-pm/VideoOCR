import os
import uuid
import asyncio
import subprocess
import json
import shutil
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from difflib import SequenceMatcher

# Try importing paddleocr, gracefully fallback to None if not installed
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


app = FastAPI(title="VideoOCR Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory setup
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
FRAMES_DIR = BASE_DIR / "frames"
UPLOAD_DIR.mkdir(exist_ok=True)
FRAMES_DIR.mkdir(exist_ok=True)

# Global state
processing_state = {
    "active": False,
    "progress": 0,
    "current_frame": 0,
    "total_frames": 0,
    "skipped_blur": 0,
    "text_blocks": [],
    "cancel_requested": False,
    "error": None,
    "video_path": None,
    "config": None,
    "language": "en",
    "session_dir": None,
}

executor = ThreadPoolExecutor(max_workers=2)


class ProcessConfig(BaseModel):
    video_path: str
    start_time: float
    end_time: float
    fps: float
    blur_threshold: int = 100
    ocr_engine: str = "paddle"
    deduplicate: bool = True
    language: str = "en"


def get_video_metadata(video_path: str) -> dict:
    """Extract video metadata using FFmpeg."""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)

        video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
        format_info = data.get("format", {})

        if not video_stream:
            raise ValueError("No video stream found in file")

        duration = float(format_info.get("duration", 0))
        width = video_stream.get("width", 0)
        height = video_stream.get("height", 0)
        fps_str = video_stream.get("r_frame_rate", "30/1")
        fps_parts = fps_str.split("/")
        fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else float(fps_parts[0])

        return {
            "duration": round(duration, 3),
            "resolution": f"{width}x{height}",
            "fps": round(fps, 2),
            "size_bytes": int(format_info.get("size", 0)),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read video metadata: {str(e)}")


def calculate_laplacian_variance(frame: np.ndarray) -> float:
    """Calculate sharpness score using Laplacian variance."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def extract_frames(video_path: str, start_time: float, end_time: float, fps: float, output_dir: str) -> list:
    """Extract frames from video at specified FPS using FFmpeg."""
    duration = end_time - start_time

    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "ffmpeg", "-y", "-ss", str(start_time), "-i", video_path,
        "-t", str(duration), "-vf", f"fps={fps}",
        "-q:v", "2", "-frame_pts", "1",
        os.path.join(output_dir, "frame_%05d.jpg")
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr}")

    frames = sorted(Path(output_dir).glob("frame_*.jpg"))
    return [str(f) for f in frames]


def get_frame_timestamp(frame_path: str, start_time: float = 0) -> float:
    """Extract timestamp from frame filename."""
    filename = Path(frame_path).stem
    try:
        pts = int(filename.split("_")[1])
        return pts / 100000.0 + start_time
    except (IndexError, ValueError):
        return start_time


def ocr_with_paddle(frame_path: str, lang: str = "en") -> str:
    """Run PaddleOCR on a frame."""
    lang_map = {"en": "en", "hi": "hi", "en_hi": "ch"}
    ocr_lang = lang_map.get(lang, "en")

    ocr = PaddleOCR(use_angle_cls=True, lang=ocr_lang, show_log=False, use_gpu=False)
    result = ocr.ocr(frame_path, cls=True)

    if not result or not result[0]:
        return ""

    texts = []
    for line in result[0]:
        if line and len(line) >= 2:
            entry = line[1]
            text = entry[0] if isinstance(entry, (list, tuple)) else str(entry)
            texts.append(text)

    return "\n".join(texts)


def ocr_with_tesseract(frame_path: str, lang: str = "en") -> str:
    """Run Tesseract OCR on a frame."""
    lang_map = {"en": "eng", "hi": "hin", "en_hi": "eng+hin"}
    tesseract_lang = lang_map.get(lang, "eng")

    img = cv2.imread(frame_path)
    if img is None:
        return ""
    text = pytesseract.image_to_string(img, lang=tesseract_lang)
    return text.strip()


def is_similar_text(text1: str, text2: str, threshold: float = 0.1) -> bool:
    """Check if text changed by less than threshold percentage."""
    if not text1 or not text2:
        return text1 == text2
    ratio = SequenceMatcher(None, text1, text2).ratio()
    return ratio > (1 - threshold)


async def process_video(config: ProcessConfig):
    """Async processing of video frames."""
    global processing_state

    try:
        processing_state["active"] = True
        processing_state["progress"] = 0
        processing_state["current_frame"] = 0
        processing_state["skipped_blur"] = 0
        processing_state["text_blocks"] = []
        processing_state["cancel_requested"] = False
        processing_state["error"] = None
        processing_state["language"] = config.language

        session_dir = FRAMES_DIR / str(uuid.uuid4())
        session_dir.mkdir(exist_ok=True)
        processing_state["session_dir"] = str(session_dir)

        # Extract frames
        frames = extract_frames(
            config.video_path,
            config.start_time,
            config.end_time,
            config.fps,
            str(session_dir)
        )

        processing_state["total_frames"] = len(frames)

        if len(frames) == 0:
            processing_state["active"] = False
            processing_state["error"] = "No frames extracted. Check video and settings."
            return

        # Setup OCR engine
        if config.ocr_engine == "paddle":
            if not PADDLEOCR_AVAILABLE:
                raise Exception("PaddleOCR is not installed. Run: pip install paddleocr paddlepaddle")
            ocr_func = lambda f: ocr_with_paddle(f, config.language)
        else:
            if not TESSERACT_AVAILABLE:
                raise Exception("Tesseract is not installed. Install tesseract and pytesseract.")
            ocr_func = lambda f: ocr_with_tesseract(f, config.language)

        prev_text = ""
        frame_counter = 0

        for i, frame_path in enumerate(frames):
            if processing_state["cancel_requested"]:
                break

            # Check blur
            img = cv2.imread(frame_path)
            if img is None:
                processing_state["current_frame"] = i + 1
                processing_state["progress"] = int((i + 1) / len(frames) * 100)
                continue

            sharpness = calculate_laplacian_variance(img)

            if sharpness < config.blur_threshold:
                processing_state["skipped_blur"] += 1
                processing_state["current_frame"] = i + 1
                processing_state["progress"] = int((i + 1) / len(frames) * 100)
                continue

            # Run OCR
            try:
                text = ocr_func(frame_path)
            except Exception as e:
                text = ""

            # Deduplicate if enabled
            if config.deduplicate and is_similar_text(prev_text, text):
                processing_state["current_frame"] = i + 1
                processing_state["progress"] = int((i + 1) / len(frames) * 100)
                continue

            frame_counter += 1
            timestamp = get_frame_timestamp(frame_path, config.start_time)

            block = {
                "frame_number": frame_counter,
                "timestamp": round(timestamp, 3),
                "text": text,
                "sharpness_score": round(sharpness, 2),
                "frame_index": i + 1,
                "frame_path": frame_path,
            }

            processing_state["text_blocks"].append(block)
            prev_text = text

            processing_state["current_frame"] = i + 1
            processing_state["progress"] = int((i + 1) / len(frames) * 100)

            await asyncio.sleep(0.001)

        processing_state["active"] = False
        processing_state["progress"] = 100

    except Exception as e:
        processing_state["active"] = False
        processing_state["error"] = str(e)


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file."""
    if file.size and file.size > 2 * 1024 * 1024 * 1024:
        return JSONResponse({"error": "File too large. Maximum size is 2GB."}, status_code=413)

    ext = Path(file.filename).suffix.lower()
    if ext not in [".mp4", ".mov", ".avi", ".webm"]:
        return JSONResponse({"error": f"Unsupported format: {ext}. Use mp4, mov, avi, or webm."}, status_code=400)

    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}{ext}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        metadata = get_video_metadata(str(file_path))

        if metadata["duration"] > 3600:
            os.remove(file_path)
            return JSONResponse({
                "error": "Video too long. Maximum duration is 60 minutes.",
            }, status_code=400)

        return {
            "file_path": str(file_path),
            "file_id": file_id,
            "metadata": metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        return JSONResponse({"error": str(e)}, status_code=400)


@app.post("/process")
async def process_video_endpoint(config: ProcessConfig):
    """Start video processing."""
    global processing_state

    if processing_state["active"]:
        return JSONResponse({"error": "Processing already in progress"}, status_code=409)

    if not os.path.exists(config.video_path):
        return JSONResponse({"error": "Video file not found"}, status_code=404)

    # Reset state
    processing_state["video_path"] = config.video_path
    processing_state["config"] = config.model_dump()

    # Run processing in background
    asyncio.create_task(process_video(config))

    return {"status": "started", "message": "Processing started"}


@app.get("/progress")
async def get_progress():
    """Get current processing progress."""
    return {
        "active": processing_state["active"],
        "progress": processing_state["progress"],
        "current_frame": processing_state["current_frame"],
        "total_frames": processing_state["total_frames"],
        "skipped_blur": processing_state["skipped_blur"],
        "text_blocks": [
            {k: v for k, v in b.items() if k != "frame_path"}
            for b in processing_state["text_blocks"]
        ],
        "error": processing_state["error"],
    }


@app.post("/cancel")
async def cancel_processing():
    """Cancel current processing."""
    processing_state["cancel_requested"] = True
    return {"status": "cancelled"}


@app.get("/frames/{frame_index}")
async def get_frame(frame_index: int):
    """Get a specific frame image."""
    session_dir = processing_state.get("session_dir")
    if not session_dir:
        return JSONResponse({"error": "No active session"}, status_code=404)

    frame_path = Path(session_dir) / f"frame_{frame_index:05d}.jpg"
    if frame_path.exists():
        return FileResponse(frame_path)

    return JSONResponse({"error": "Frame not found"}, status_code=404)


@app.get("/results")
async def get_results():
    """Get final processing results."""
    results = [
        {k: v for k, v in b.items() if k != "frame_path"}
        for b in processing_state["text_blocks"]
    ]
    return {"results": results}


@app.get("/status")
async def get_status():
    """Get system status and available OCR engines."""
    ffmpeg_ok = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=10).returncode == 0

    return {
        "paddleocr_available": PADDLEOCR_AVAILABLE,
        "tesseract_available": TESSERACT_AVAILABLE,
        "ffmpeg_available": ffmpeg_ok,
    }


@app.delete("/cleanup")
async def cleanup():
    """Clean up session frames."""
    session_dir = processing_state.get("session_dir")
    if session_dir and Path(session_dir).exists():
        shutil.rmtree(session_dir)
    processing_state["session_dir"] = None
    processing_state["text_blocks"] = []
    return {"status": "cleaned"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)