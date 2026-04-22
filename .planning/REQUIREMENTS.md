# Requirements: VideoOCR Studio

**Defined:** 2026-04-22
**Core Value:** Users can extract readable text from video recordings of documents (scrolling lectures, whiteboard videos, scanned page videos) using configurable OCR with frame quality filtering and deduplication.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Backend - Upload & Storage

- [x] **BACK-01**: Accept video file upload via POST /upload endpoint
- [x] **BACK-02**: Validate video file format (.mp4, .mov, .avi, .webm)
- [x] **BACK-03**: Store uploaded video in temp directory with unique session ID
- [x] **BACK-04**: Return video metadata (duration, resolution, FPS) after upload
- [x] **BACK-05**: Warn if file exceeds 2GB
- [x] **BACK-06**: Warn if video duration exceeds 60 minutes

### Backend - Frame Extraction

- [x] **BACK-07**: Accept processing config via POST /process with all parameters   
- [x] **BACK-08**: Use FFmpeg subprocess to extract frames at specified FPS within time range
- [x] **BACK-09**: Score frames for sharpness using OpenCV Laplacian variance       
- [x] **BACK-10**: Skip frames below blur threshold (configurable, default 100)     
- [x] **BACK-11**: Run PaddleOCR (primary) or Tesseract (fallback) on remaining frames
- [x] **BACK-12**: Deduplication removes consecutive frames with <10% text change using difflib
- [x] **BACK-13**: Return structured JSON: list of {frame_number, timestamp, text, sharpness_score}
- [x] **BACK-14**: Serve frame images via GET /frame/{frame_number} endpoint        

### Backend - Progress Streaming

- [x] **BACK-15**: Stream progress via GET /progress using SSE
- [x] **BACK-16**: Include percent done, current frame number, frames skipped, extracted text
- [x] **BACK-17**: Implement heartbeat to prevent SSE stalls
- [x] **BACK-18**: Return terminal event (complete/failed) when processing ends     

### Backend - Error Handling

- [x] **BACK-19**: Detect and report FFmpeg not found
- [x] **BACK-20**: Detect and report unsupported video codec
- [x] **BACK-21**: Detect and report OCR engine not installed
- [x] **BACK-22**: Return user-friendly error messages (not raw stack traces)       

### Frontend - Upload Panel

- [x] **FRONT-01**: Drag-and-drop video upload area
- [x] **FRONT-02**: Click-to-upload fallback
- [x] **FRONT-03**: Show video thumbnail preview after upload
- [x] **FRONT-04**: Display video metadata: duration, resolution, detected FPS

### Frontend - Video Range Selector

- [x] **FRONT-05**: Interactive timeline scrubber showing full video duration
- [x] **FRONT-06**: Two draggable handles for START and END time markers
- [x] **FRONT-07**: Real-time timecode display (MM:SS) for both handles
- [x] **FRONT-08**: Preview frame thumbnail that updates during scrubbing
- [x] **FRONT-09**: Quick presets: "First 2 min", "First 5 min", "Full video"

### Frontend - Frame Rate Selector

- [x] **FRONT-10**: Horizontal slider from 0.5 fps to 30 fps
- [x] **FRONT-11**: Labeled stops at 0.5, 1, 2, 5, 10, 15, 30
- [x] **FRONT-12**: Show estimated frame count and processing time
- [x] **FRONT-13**: Warning badge when frame count exceeds 5000

### Frontend - Advanced Options

- [x] **FRONT-14**: Blur threshold slider (0-300, default 100) with label
- [x] **FRONT-15**: OCR engine toggle: PaddleOCR vs Tesseract
- [x] **FRONT-16**: Deduplicate toggle (on by default)
- [x] **FRONT-17**: Language selector dropdown (English, Hindi, English+Hindi)
- [x] **FRONT-18**: Collapsible advanced options section

### Frontend - Process Controls

- [x] **FRONT-19
**: Large "Extract Text" primary button
- [x] **FRONT-20
**: Disabled state during processing with spinner
- [x] **FRONT-21
**: Show "Processing frame X of Y" status during extraction

### Frontend - Progress Panel

- [x] **FRONT-22
**: Animated progress bar
- [x] **FRONT-23
**: Live stats: Frames Processed | Frames Skipped | Text Blocks Found
- [ ] **FRONT-24**: Scrollable live text output (auto-scrolls to bottom)
- [x] **FRONT-25
**: Cancel button to abort processing

### Frontend - Output Validation Panel

- [ ] **FRONT-26**: Split view: Frame Browser (left) + Text Output (right)
- [ ] **FRONT-27**: Vertical strip of thumbnail images from /frame/{n}
- [ ] **FRONT-28**: Click frame to highlight and show its extracted text
- [ ] **FRONT-29**: Editable full text area for user corrections
- [ ] **FRONT-30**: Sharpness score badge on thumbnails (green=sharp, yellow=ok, red=blurry)
- [ ] **FRONT-31**: Export options: Copy All Text, .txt, .md, .docx
- [ ] **FRONT-32**: "Re-process selected range" button

### Frontend - Design

- [x] **FRONT-33**: Dark-mode first with light mode toggle
- [x] **FRONT-34**: Color scheme: deep dark surfaces (#0f0e0c, #141312), teal accent (#01696f)      
- [x] **FRONT-35**: Monospace font for text output (JetBrains Mono via CDN)
- [x] **FRONT-36**: Sans-serif UI font (Satoshi via Fontshare)
- [x] **FRONT-37**: Left sidebar (controls) + main content area (output) layout
- [ ] **FRONT-38**: Film-strip aesthetic for frame thumbnails
- [ ] **FRONT-39**: Smooth transitions for panel state changes

### Documentation

- [ ] **DOCS-01**: requirements.txt with all Python dependencies
- [ ] **DOCS-02**: README.md with prerequisites, install steps, run instructions    

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Batch Processing

- **BATCH-01**: Queue multiple videos for sequential processing
- **BATCH-02**: Background processing with notification on completion

### Export Formats

- **EXPORT-01**: JSON export with full metadata
- **EXPORT-02**: SRT subtitle format
- **EXPORT-03**: PDF with embedded text

### Advanced OCR

- **OCR-01**: EasyOCR as additional engine option
- **OCR-02**: Confidence scoring per text block
- **OCR-03**: Text overlay preview on frames

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Cloud deployment | Fully local operation for privacy |
| Video editing | Not a video editor, just OCR extraction |
| Batch queue UI | Defer to v2; single video processing is primary use case |       
| Mobile UI | Desktop utility app, mobile not a target |
| Non-English OCR beyond English/Hindi | Scope constraint from requirements |       
| Real-time processing | Not streaming; batch frame-by-frame |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BACK-01 to BACK-22 | Phase 1: Backend Foundation | Complete |
| DOCS-01 to DOCS-02 | Phase 1: Backend Foundation | Pending |
| FRONT-01 to FRONT-18 | Phase 2: Frontend Core | Complete |
| FRONT-19 to FRONT-32 | Phase 3: Processing Pipeline | Pending |
| FRONT-33 to FRONT-39 | Phase 4: Output & Polish | Pending |

**Coverage:**
- v1 requirements: 57 total
- Mapped to phases: 57
- Unmapped: 0

---
*Requirements defined: 2026-04-22*
*Last updated: 2026-04-22 (Phase 1 & 2 Completed)*
