# Project Research Summary

**Project:** VideoOCR Studio
**Domain:** Local Video OCR Application with Web UI
**Researched:** 2026-04-22
**Confidence:** MEDIUM-HIGH

## Executive Summary

VideoOCR Studio is a local-first video OCR tool that extracts text from screen recordings and document videos. Unlike cloud-based alternatives, it processes everything on-device for privacy and offline use. The recommended stack uses FastAPI for the backend API, PaddleOCR as the primary OCR engine with Tesseract as fallback, OpenCV for frame processing, and FFmpeg via subprocess for video decoding. The frontend is a self-contained static HTML/CSS/JS application.

Research indicates this is a well-solved problem domain with established patterns: use job queues with SSE for progress streaming, implement frame deduplication before OCR to avoid processing 80-95% duplicate frames, and apply quality gates (blur detection, resolution checks) before sending frames to OCR. The biggest risks are FFmpeg integration fragility, memory exhaustion on large videos, and SSE connection stalls. These are all preventable with proper architecture: chunked processing, informative error handling, and heartbeat-based connection monitoring.

## Key Findings

### Recommended Stack

FastAPI with uvicorn provides the backend API layer with native async support critical for long-running video processing. PaddleOCR 2.9.x handles challenging text (rotated, mixed scripts) better than Tesseract, while Tesseract serves as a stable fallback for simple well-aligned text. OpenCV handles frame preprocessing and blur detection. FFmpeg must be invoked via subprocess -- not the abandoned ffmpeg-python library.

**Core technologies:**
- **FastAPI 0.128.0 + uvicorn 0.32.x:** REST API backend with native async; automatic OpenAPI docs
- **PaddleOCR 2.9.x:** Primary OCR engine; better accuracy on rotated/mixed text than alternatives
- **pytesseract 0.3.x:** Fallback OCR wrapper; mature and stable
- **OpenCV 4.12.x:** Video/frame processing; Laplacian blur detection for quality filtering
- **FFmpeg (system-level):** Video decoding via subprocess (NOT ffmpeg-python)

### Expected Features

**Must have (table stakes):**
- Video file import (MP4, AVI, MOV, MKV, WebM) -- drag-drop support expected
- Frame extraction at configurable rate -- essential for controlling output quality
- Time range selection (start/end) -- isolate relevant segments
- Tesseract OCR engine -- proven, well-documented, local
- TXT text output -- fundamental deliverable
- Progress indication -- long video processing requires feedback

**Should have (competitive):**
- Timestamp synchronization -- users need to verify accuracy and find context in video
- CSV export with timestamps -- natural extension of timestamp sync
- Blur detection with threshold slider -- critical for lower-quality input video
- Smart frame sampling -- skip visually identical frames; biggest workflow efficiency win

**Defer (v2+):**
- Multiple OCR engine support -- adds significant UI complexity, validate user demand first
- Confidence scoring -- secondary quality signal
- Batch processing -- productivity feature for power users
- JSON export -- downstream tool integration

### Architecture Approach

The architecture follows a service layer pattern with clear component boundaries. The backend uses FastAPI with routes separated by domain (upload, frames, ocr, progress), services containing business logic, and workers handling CPU-intensive operations (FFmpeg frame extraction, OCR processing). The frontend uses a VideoContext with reducer pattern for state management, communicating with the backend via REST API and SSE for progress streaming.

**Major components:**
1. **Upload Handler:** Receives video file, validates format, initiates session
2. **Frame Extractor:** Decodes video, extracts frames at timestamps using FFmpeg subprocess
3. **OCR Engine:** Processes frames via PaddleOCR/Tesseract; includes quality gates and deduplication
4. **Progress Tracker:** Emits SSE events for long-running operations with heartbeat
5. **Session Manager:** Tracks state across requests; stores results in SQLite
6. **State Manager (Frontend):** VideoContext with useReducer for reactive UI state

### Critical Pitfalls

1. **Ignoring frame quality before OCR:** OCR runs on every frame regardless of quality, producing garbage from blurry/low-res frames. Prevention: Implement pre-OCR quality gate (Laplacian variance < threshold, resolution check) and reject frames BEFORE sending to OCR engine.

2. **No frame deduplication:** Video has 24-60fps; most consecutive frames contain identical text. Processing all frames wastes 80-95% of compute. Prevention: Implement perceptual hashing (pHash) comparison; only run OCR on frames differing by > threshold.

3. **Memory exhaustion with large videos:** Loading 2GB+ videos and storing all frames in memory causes OOM crashes. Prevention: Process frames in bounded chunks, release VideoCapture objects immediately, limit OCR concurrency to 1-2 instances.

4. **FFmpeg integration fragility:** FFmpeg commands fail silently with codec issues or empty outputs. Prevention: Capture both stdout AND stderr, check return codes explicitly, use ffprobe to validate video before processing.

5. **SSE progress updates stop working:** Frontend shows "Processing..." forever when SSE disconnects. Prevention: Implement heartbeat every 5-10 seconds, track background task state, include terminal "complete/failed" event.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Backend Foundation
**Rationale:** All other phases depend on having a working backend. This phase establishes the foundation and addresses critical pitfalls 3, 4, 7 (memory management, FFmpeg integration, path handling).
**Delivers:** File storage service, session database, upload endpoint, validated FFmpeg integration, cross-platform path handling
**Addresses:** Stack elements (FastAPI, uvicorn, SQLite), architecture components (Upload Handler, Session Manager)
**Avoids:** Hardcoded paths failing on user machines; FFmpeg codec errors appearing silently; OOM on large videos

### Phase 2: Frame Extraction and Quality Pipeline
**Rationale:** Frame extraction is the foundation of OCR accuracy. Must implement quality gates and deduplication here, not as post-processing. Addresses pitfalls 1, 2, 6.
**Delivers:** Frame extraction worker, blur detection, perceptual hash deduplication, OCR configuration (PSM 11 for sparse text)
**Addresses:** P1 features (configurable frame rate), P2 features (blur detection, smart sampling)
**Uses:** FFmpeg subprocess, OpenCV, PaddleOCR/Tesseract with proper config
**Implements:** Frame Extractor component with quality gates

### Phase 3: Frontend Core - Video Playback
**Rationale:** Need working video player before users can select frames. Depends on Phase 1 upload and static file serving.
**Delivers:** Static file serving, video player component, upload widget with drag-drop
**Addresses:** P1 features (video import, progress indication)
**Uses:** HTML5 Video element with canvas overlay
**Implements:** Timeline Scrubber foundation

### Phase 4: Frontend - Frame Selection UI
**Rationale:** Frame selection is the primary user interaction pattern. Depends on video playback working.
**Delivers:** Timeline scrubber with visual seeking, frame selector to capture timestamps, selection management (view/remove selected frames)
**Addresses:** P1 features (time range selection)
**Uses:** VideoContext state management
**Implements:** Frame Selector component

### Phase 5: Processing Pipeline and Progress
**Rationale:** Core workflow: user selects frames -> triggers OCR -> sees results. Must implement job queue with background workers and SSE progress streaming. Addresses pitfalls 5, 8.
**Delivers:** Job queue with background workers, SSE progress streaming with heartbeat, progress display component, checkpointing for resume capability
**Addresses:** P1 features (progress indication), P2 features (timestamp sync, CSV export)
**Uses:** FastAPI BackgroundTasks, ThreadPoolExecutor
**Implements:** Progress Tracker component, job state persistence

### Phase 6: Output and Polish
**Rationale:** Final UX phase. Users need to see results and export them. Depends on Phase 5 processing pipeline.
**Delivers:** Results display with timestamp labels, TXT and CSV export, error handling with retry options, basic settings UI
**Addresses:** P1 features (text output to file), P2 features (CSV with timestamps)
**Uses:** Service layer patterns for export formatting
**Implements:** Output component

### Phase Ordering Rationale

- **Backend first:** Frontend cannot function without API endpoints. Phase 1 establishes the contract.
- **Frame quality pipeline early:** Deduplication and quality gates must be built into extraction, not retrofitted. Waiting until Phase 5 means rewriting Phase 2.
- **Frontend core before frame selection:** Need working video player before users can scrub timeline to select frames.
- **Processing pipeline last:** Depends on both backend (job queue) and frontend (progress display) being working.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Frame Extraction):** FFmpeg codec detection and validation logic needs specific implementation research
- **Phase 5 (Processing Pipeline):** SSE reconnection patterns and job queue persistence need API design research

Phases with standard patterns (skip research-phase):
- **Phase 1 (Backend Foundation):** FastAPI + SQLite patterns are well-documented, use standard service layer
- **Phase 6 (Output):** Export formatting is standard CRUD, no novel patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified from PyPI with specific versions; alternatives clearly documented |
| Features | MEDIUM | Based on competitor analysis and user forum research; feature set is reasonable but not web-verified |
| Architecture | MEDIUM | Based on established patterns (FastAPI docs, service layer, SSE patterns); not web-verified |
| Pitfalls | MEDIUM-HIGH | Based on documented OCR/video processing pitfalls; some sourced from GitHub issues and Stack Overflow |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **PaddleOCR vs Tesseract split:** Research recommends PaddleOCR primary but MVP could ship with Tesseract only. Need to decide during planning whether to implement dual-engine or defer.
- **Blur detection threshold calibration:** No specific threshold value recommended. Need to test with sample videos during implementation.
- **Perceptual hash threshold:** Dedup threshold (pHash hamming distance > 10) is suggested but not validated. Need calibration during implementation.

## Sources

### Primary (HIGH confidence)
- FastAPI official documentation -- async patterns, SSE, background tasks
- PaddleOCR GitHub (PaddlePaddle/PaddleOCR) -- v2.9.x model configuration, accuracy notes
- PyPI package versions -- numpy 2.3.5 (yanked 2.4.0), opencv-python 4.12.x compatibility
- Tesseract documentation -- PSM modes and OEM configuration for sparse text

### Secondary (MEDIUM confidence)
- SubtitleEdit feature reference -- competitor analysis for feature gaps
- FFmpeg documentation -- codec compatibility notes
- OpenCV VideoCapture memory management -- bounded chunk processing patterns
- FastAPI SSE implementation patterns -- community examples for heartbeat and reconnection

### Tertiary (LOW confidence)
- Perceptual hash threshold value -- suggested 10 but needs validation
- Blur detection threshold -- suggested but needs calibration
- Large video memory budgets -- general guidance but no specific numbers

---
*Research completed: 2026-04-22*
*Ready for roadmap: yes*