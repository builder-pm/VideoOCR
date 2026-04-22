# VideoOCR Studio

## Project Overview

A local desktop utility web app for extracting text from scrolling document videos using open-source OCR tools (FFmpeg + PaddleOCR/Tesseract). Consists of a vanilla HTML/CSS/JS frontend communicating with a Python FastAPI backend.

**Core Value:** Users can extract readable text from video recordings of documents (scrolling lectures, whiteboard videos, scanned page videos) using configurable OCR with frame quality filtering and deduplication.

**Stack:**
- Frontend: Vanilla HTML/CSS/JS (single file: `videocr-studio.html`)
- Backend: Python FastAPI + uvicorn (`server.py`)
- OCR: PaddleOCR (primary), Tesseract (fallback)
- Video: FFmpeg (system install) + OpenCV for frame analysis
- Dedup: difflib SequenceMatcher for <10% text change detection

## Workflow

This project uses the GSD (Get Shit Done) workflow.

### Commands

- `/gsd-plan-phase N` — Plan phase N (creates PLAN.md)
- `/gsd-execute-phase N` — Execute phase N plans
- `/gsd-discuss-phase N` — Discuss phase N approach before planning
- `/gsd-progress` — Show project status
- `/gsd-next` — Advance to next logical step

### Phase Order

1. **Phase 1: Backend Foundation** — API, upload, frame extraction, SSE streaming, error handling
2. **Phase 2: Frontend Core** — Upload panel, video preview, timeline scrubber, controls
3. **Phase 3: Processing Pipeline** — Process controls, progress display, output validation
4. **Phase 4: Output & Polish** — Design system, dark/light mode, typography, documentation

### Config

- **Mode:** YOLO (auto-approve plans)
- **Granularity:** Coarse (4 phases)
- **Parallelization:** Enabled
- **Git Tracking:** Enabled
- **Research:** Before planning each phase
- **Plan Check:** Verify plans achieve goals
- **Verifier:** Confirm deliverables match requirements

## Requirements

See `.planning/REQUIREMENTS.md` for full requirement list (57 v1 requirements).

Key requirements:
- Upload: POST /upload, validate .mp4/.mov/.avi/.webm, warn >2GB or >60min
- Process: POST /process with config (start_time, end_time, fps, blur_threshold, ocr_engine, deduplicate)
- Frames: Extract via FFmpeg, score sharpness via OpenCV Laplacian, skip blurry frames
- OCR: PaddleOCR primary, Tesseract fallback
- Deduplication: Skip frames with <10% text change
- Progress: GET /progress via SSE with heartbeat
- Output: JSON with {frame_number, timestamp, text, sharpness_score}
- Frames: GET /frame/{frame_number} for preview

## Design

- Dark-mode first with light mode toggle
- Colors: #0f0e0c (deep dark), #141312 (surface), #01696f (teal accent)
- Fonts: JetBrains Mono (monospace via CDN), Satoshi (UI via Fontshare)
- Layout: Left sidebar (controls) + main content (output)
- Frame thumbnails: Film-strip aesthetic

## Architecture

See `.planning/research/ARCHITECTURE.md` for component boundaries and data flow.

Key patterns:
- Service layer pattern for business logic
- SSE for one-way progress streaming (no WebSocket complexity)
- BackgroundTasks for CPU-intensive operations
- SQLite for session state (simple, local)

## Critical Patterns

See `.planning/research/PITFALLS.md` for critical pitfalls to avoid:

1. **Pre-OCR quality gates** — Blur detection before OCR, not after
2. **Frame deduplication** — Skip visually identical frames (80-95% compute savings)
3. **Memory management** — Chunked processing, release VideoCapture immediately
4. **FFmpeg error handling** — Capture stderr, check return codes, use ffprobe
5. **SSE heartbeat** — Every 5-10 seconds to prevent "stuck" appearance

## Files

- `server.py` — FastAPI backend (in progress)
- `videocr-studio.html` — Frontend (needs creation)
- `requirements.txt` — Python dependencies
- `README.md` — Setup instructions (needs creation)
- `.planning/` — Project planning artifacts

## Getting Started

Run: `uvicorn server:app --reload`
Frontend auto-connects to `http://localhost:8000`

**Prerequisites:** Python 3.10+, FFmpeg (system), PaddleOCR/Tesseract (pip)