# VideoOCR Studio

## What This Is

A local desktop utility web app for extracting text from scrolling document videos using open-source OCR tools. The app consists of a vanilla HTML/CSS/JS frontend that communicates with a Python FastAPI backend, providing visual frame-by-frame text extraction with real-time progress feedback.

## Core Value

Users can extract readable text from video recordings of documents (scrolling lectures, whiteboard videos, scanned page videos) using configurable OCR with frame quality filtering and deduplication.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Video file upload with drag-and-drop support
- [ ] Video metadata extraction (duration, resolution, FPS)
- [ ] Interactive timeline scrubber with START/END handles
- [ ] Quick presets for time range selection
- [ ] Frame rate slider with estimated processing time
- [ ] Blur threshold configuration (Laplacian variance)
- [ ] OCR engine toggle (PaddleOCR / Tesseract)
- [ ] Language selection (English, Hindi, English+Hindi)
- [ ] Deduplication toggle for near-identical frames
- [ ] Real-time SSE progress streaming
- [ ] Frame browser with sharpness score badges
- [ ] Editable text output with copy/export options
- [ ] Error handling for FFmpeg, video codec, OCR engine issues

### Out of Scope

- Cloud deployment — fully local operation
- Video editing or trimming features
- Batch processing multiple videos
- Mobile-optimized UI
- Non-English OCR beyond English/Hindi

## Context

The project starts with an existing `server.py` skeleton and `requirements.txt`. The existing code provides a basic FastAPI server structure that needs to be completed and integrated with the frontend.

**Existing files:**
- `server.py` — partial FastAPI backend (needs completion)
- `requirements.txt` — Python dependencies

**Missing files to create:**
- `videocr-studio.html` — complete frontend
- `README.md` — setup instructions

## Constraints

- **Tech Stack**: Vanilla HTML/CSS/JS (no frameworks), Python FastAPI, FFmpeg, OpenCV, PaddleOCR/Tesseract
- **Local Only**: No cloud services, all processing on user's machine
- **File Size**: Warn if > 2GB
- **Duration**: Warn if > 60 minutes
- **Video Formats**: .mp4, .mov, .avi, .webm

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Vanilla HTML frontend | No build step, easy to distribute, single file | — Pending |
| PaddleOCR primary, Tesseract fallback | PaddleOCR handles rotated/mixed text better | — Pending |
| SSE for progress streaming | Real-time feedback without WebSocket complexity | — Pending |
| Dark-mode first | Tool-like utility aesthetic, reduces eye strain | — Pending |

---

*Last updated: 2026-04-22 after initialization*

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state