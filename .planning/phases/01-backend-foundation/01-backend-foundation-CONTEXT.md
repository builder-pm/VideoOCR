# Phase 1: Backend Foundation - Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the core FastAPI backend that powers VideoOCR Studio:
- Video upload and storage with session management
- FFmpeg subprocess integration for frame extraction
- OpenCV-based blur detection (Laplacian variance)
- PaddleOCR (primary) and Tesseract (fallback) OCR engines
- Server-Sent Events (SSE) for real-time progress streaming
- User-friendly error handling for FFmpeg, codec, and OCR issues
- Documentation (requirements.txt, README.md)

All backend endpoints the frontend will call.

</domain>

<decisions>
## Implementation Decisions

### Architecture
- FastAPI + uvicorn for async API
- FFmpeg invoked via subprocess (NOT ffmpeg-python — abandoned)
- OpenCV for frame analysis and blur detection
- PaddleOCR 2.9.x primary, pytesseract fallback
- SQLite for session state (simple, local)

### Video Handling
- Validate .mp4, .mov, .avi, .webm formats
- Warn if > 2GB or > 60 minutes
- Store in temp directory with UUID session ID
- Use ffprobe for metadata extraction

### Frame Processing Pipeline
- Extract frames at configurable FPS via FFmpeg subprocess
- Score sharpness using cv2.Laplacian variance
- Skip frames below blur threshold (default 100, configurable 0-300)
- Run OCR on remaining frames
- Deduplicate: skip frames with <10% text change (difflib SequenceMatcher)

### Progress Streaming
- SSE via FastAPI StreamingResponse
- Heartbeat every 5-10 seconds to prevent stalls
- Terminal event (complete/failed) when processing ends

### Error Handling
- Detect FFmpeg not found
- Detect unsupported video codec
- Detect OCR engine not installed
- Return user-friendly messages (not stack traces)

### Claude's Discretion
All specific implementation details are at developer's discretion — FastAPI patterns, exact function signatures, data structures, file organization.

</decisions>

<code_context>
## Existing Code Insights

### Existing Files
- `server.py` — partial FastAPI backend (needs completion)
- `requirements.txt` — Python dependencies

### No Frontend Yet
This phase is pure backend. Frontend integration comes in Phase 2+.

### Patterns to Reuse
Standard FastAPI patterns: dependencies, BackgroundTasks, StreamingResponse
Standard file handling patterns for temp storage

</code_context>

<specifics>
## Specific Ideas

No specific requirements beyond the functional specs in ROADMAP.md.
Use FastAPI best practices, async patterns, proper error handling.

</specifics>

<deferred>
## Deferred Ideas

None — Phase 1 is self-contained backend work.

</deferred