# VideoOCR Studio Backend

FastAPI-based backend for high-performance video frame extraction and OCR.

## Features
- **Session Management:** Isolated processing for multiple concurrent users.
- **Real-time Progress:** Live updates via Server-Sent Events (SSE).
- **Processing Pipeline:** Automated frame extraction, blur detection, and deduplication.
- **Multiple OCR Engines:** Support for Tesseract and PaddleOCR.

## Prerequisites

### 1. FFmpeg (Required)
Essential for video handling.
- **Windows:** `winget install Gyan.FFmpeg`
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

### 2. OCR Engines
You need at least one of these:
- **Tesseract:** [Download here](https://github.com/UB-Mannheim/tesseract/wiki).
- **PaddleOCR:** Installed via pip (see below). *Note: May require additional configuration on Windows.*

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Transideo
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install PaddleOCR (Optional):**
   ```bash
   pip install paddlepaddle paddleocr
   ```

## Running the App

Start the server:
```bash
python server.py
```
The API will be available at `http://localhost:8000`.

## Testing

Run the automated test suite:
```bash
pytest tests/test_server.py
```

Or run the real-world video verification script:
```bash
python verify_video.py
```

## API Summary
- `POST /upload`: Upload video and get `session_id`.
- `POST /process`: Start OCR processing.
- `GET /progress`: Stream progress via SSE.
- `GET /results`: Fetch final text blocks.
- `GET /status`: Check engine availability.
