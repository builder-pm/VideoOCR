# Validation Map: Phase 1 - Backend Foundation

## Requirements Coverage

| ID | Requirement | Test Type | Automated Command | Status |
|----|-------------|-----------|-------------------|--------|
| BACK-01 | Accept video file upload via POST /upload | Unit | `pytest tests/test_server.py::test_upload_video_mocked` | green |
| BACK-02 | Validate video file format (.mp4, .mov, .avi, .webm) | Unit | `pytest tests/test_server.py::test_upload_invalid_format` | red |
| BACK-03 | Store uploaded video in temp directory with unique session ID | Unit | `pytest tests/test_server.py::test_upload_video_mocked` | green |
| BACK-04 | Return video metadata (duration, resolution, FPS) after upload | Unit | `pytest tests/test_server.py::test_upload_video_mocked` | green |
| BACK-05 | Warn if file exceeds 2GB | Unit | `pytest tests/test_server.py::test_upload_file_too_large` | red |
| BACK-06 | Warn if video duration exceeds 60 minutes | Unit | `pytest tests/test_server.py::test_upload_too_long` | green |
| BACK-07 | Accept processing config via POST /process | Unit | `pytest tests/test_server.py::test_process_start` | green |
| BACK-08 | Use FFmpeg to extract frames | Integration | `pytest tests/test_server.py::test_extract_frames` | red |
| BACK-09 | Score frames for sharpness (Laplacian) | Unit | `pytest tests/test_server.py::test_sharpness_calculation` | red |
| BACK-10 | Skip frames below blur threshold | Integration | `pytest tests/test_server.py::test_blur_skipping` | red |
| BACK-11 | Run PaddleOCR or Tesseract on frames | Integration | `pytest tests/test_server.py::test_ocr_integration` | red |
| BACK-12 | Deduplicate frames with <10% text change | Unit | `pytest tests/test_server.py::test_text_deduplication` | red |
| BACK-13 | Return structured JSON with frame data | Unit | `pytest tests/test_server.py::test_get_results` | red |
| BACK-14 | Serve frame images via GET /frame/{n} | Unit | `pytest tests/test_server.py::test_get_frame` | red |
| BACK-15 | Stream progress via GET /progress (SSE) | Unit | `pytest tests/test_server.py::test_sse_progress` | green |
| BACK-16 | Include percent, frame #, skipped, text in SSE | Unit | `pytest tests/test_server.py::test_sse_progress` | green |
| BACK-17 | Implement heartbeat in SSE | Unit | `pytest tests/test_server.py::test_sse_heartbeat` | red |
| BACK-18 | Return terminal event when processing ends | Unit | `pytest tests/test_server.py::test_sse_terminal_event` | red |
| BACK-19 | Detect and report FFmpeg not found | Unit | `pytest tests/test_server.py::test_status_endpoint` | green |
| BACK-20 | Detect and report unsupported video codec | Unit | `pytest tests/test_server.py::test_invalid_video_metadata` | red |
| BACK-21 | Detect and report OCR engine not installed | Unit | `pytest tests/test_server.py::test_status_endpoint` | green |
| BACK-22 | Return user-friendly error messages | Unit | `pytest tests/test_server.py::test_friendly_errors` | red |
| DOCS-01 | requirements.txt exists | Smoke | `ls requirements.txt` | green |
| DOCS-02 | README.md exists | Smoke | `ls README.md` | green |

## Validation Results

*Pending completion of missing tests.*
