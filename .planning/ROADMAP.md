# Roadmap: VideoOCR Studio

**Granularity:** Coarse (4-5 phases)
**Created:** 2026-04-22

---

## Phases

- [x] **Phase 1: Backend Foundation** - Core backend API, upload, frame extraction, SSE streaming, error handling
- [x] **Phase 2: Frontend Core** - Upload panel, video preview, timeline scrubber, frame rate controls, advanced options
- [ ] **Phase 3: Processing Pipeline** - Process controls, progress display, output validation, frame browser, export
- [ ] **Phase 4: Output & Polish** - Design system, dark/light mode, typography, layout polish, documentation

---

## Phase Details

### Phase 1: Backend Foundation

**Goal:** Backend API can receive videos, extract frames, run OCR, and stream progress

**Depends on:** Nothing (first phase)

**Requirements:** BACK-01 to BACK-22, DOCS-01 to DOCS-02

**Success Criteria** (what must be TRUE):
1. User can upload .mp4, .mov, .avi, .webm video files via POST /upload and receive session ID
2. User receives file size warning (>2GB) or duration warning (>60min) if applicable
3. API returns video metadata (duration, resolution, FPS) after successful upload   
4. Backend extracts frames at configurable FPS using FFmpeg subprocess within time range
5. Blur detection (Laplacian variance) filters out blurry frames below configurable threshold
6. OCR runs on remaining frames using PaddleOCR (primary) or Tesseract (fallback)   
7. Deduplication removes consecutive frames with <10% text change
8. Processing progress streams to client via GET /progress SSE endpoint with heartbeat
9. User can browse extracted frames via GET /frame/{frame_number}
10. Errors return friendly messages for missing FFmpeg, unsupported codec, or missing OCR engine

**Plans:**
- [x] 01-01-PLAN.md — Session & SSE Refactor
- [x] 01-02-PLAN.md — Pipeline Robustness & Error Handling
- [x] 01-03-PLAN.md — Testing & Documentation

---

### Phase 2: Frontend Core

**Goal:** User can upload videos and configure extraction settings via a responsive UI

**Depends on:** Phase 1

**Requirements:** FRONT-01 to FRONT-18, FRONT-33 to FRONT-37

**Success Criteria** (what must be TRUE):
1. User can drag-and-drop video file onto upload area (with click fallback)
2. Uploaded video shows thumbnail preview and displays metadata (duration, resolution, FPS)
3. User can scrub through video using interactive timeline with START/END draggable handles
4. Timeline shows real-time timecode (MM:SS) and preview thumbnail updates during scrubbing
5. User can select quick presets: "First 2 min", "First 5 min", "Full video"        
6. User can adjust frame rate via horizontal slider (0.5-30fps) with labeled stops at 0.5, 1, 2, 5, 10, 15, 30
7. Estimated frame count and processing time update in real-time based on slider position
8. Warning badge appears when frame count exceeds 5000
9. Advanced options panel is collapsible and includes blur threshold slider, OCR engine toggle, language selector, deduplication toggle

**Plans:**
- [x] 02-01-PLAN.md — SPA Shell & Foundation
- [x] 02-02-PLAN.md — Upload Flow & Metadata
- [x] 02-03-PLAN.md — Timeline Range Selector
- [x] 02-04-PLAN.md — Config Controls & Estimation

**UI hint:** yes

---

### Phase 3: Processing Pipeline

**Goal:** User can trigger extraction and see real-time results with validation capabilities

**Depends on:** Phase 2

**Requirements:** FRONT-19 to FRONT-32

**Success Criteria** (what must be TRUE):
1. "Extract Text" button triggers processing and shows disabled state with spinner during execution
2. Status shows "Processing frame X of Y" updating in real-time
3. Animated progress bar fills as frames complete
4. Live stats display: Frames Processed, Frames Skipped, Text Blocks Found
5. Extracted text scrolls live in output panel (auto-scrolls to bottom)
6. User can cancel processing mid-execution
7. Frame browser shows vertical strip of thumbnails with sharpness score badges (green/yellow/red)
8. Clicking a frame thumbnail highlights it and shows extracted text in context     
9. Full text output is editable for user corrections
10. Export options available: Copy All Text, .txt, .md, .docx
11. "Re-process selected range" button allows reprocessing with different settings  

**Plans:** TBD

**UI hint:** yes

---

### Phase 4: Output & Polish

**Goal:** Application has professional visual design with working documentation     

**Depends on:** Phase 3

**Requirements:** FRONT-33 to FRONT-39, DOCS-01 to DOCS-02

**Success Criteria** (what must be TRUE):
1. Dark mode is default; user can toggle to light mode
2. Color scheme applies: deep dark surfaces (#0f0e0c, #141312), teal accent (#01696f)
3. Text output displays in JetBrains Mono (monospace, via CDN)
4. UI elements use Satoshi font (sans-serif, via Fontshare)
5. Layout follows: left sidebar for controls, main content area for output
6. Frame thumbnails have film-strip aesthetic styling
7. Panel state changes animate with smooth transitions
8. README.md documents prerequisites, installation steps, and run instructions      
9. requirements.txt lists all Python dependencies with correct versions

**Plans:** TBD

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Backend Foundation | 3/3 | Completed | 2026-04-22 |
| 2. Frontend Core | 4/4 | Completed | 2026-04-22 |
| 3. Processing Pipeline | 0/TBD | Not started | - |
| 4. Output & Polish | 0/TBD | Not started | - |

---

## Coverage

**v1 Requirements:** 57 total
- BACK-01 to BACK-22 (22) in Phase 1
- FRONT-01 to FRONT-18 (18) in Phase 2
- FRONT-19 to FRONT-32 (14) in Phase 3
- FRONT-33 to FRONT-39 (7) + DOCS-01 to DOCS-02 (2) in Phase 4

**Mapped:** 57/57 (100%)
**Unmapped:** 0

---

*Roadmap created: 2026-04-22*
*Roadmap updated: 2026-04-22 (Phase 2 completed)*
