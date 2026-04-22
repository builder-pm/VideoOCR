# Architecture Research

**Domain:** Local video processing web application (OCR extraction tool)
**Researched:** 2026-04-22
**Confidence:** MEDIUM (based on established architectural patterns; not web-verified due to search limitations)

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Upload     │  │  Timeline    │  │   Frame      │  │   Output     │    │
│  │   Widget     │  │  Scrubber    │  │  Selector    │  │  Display     │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                │                │                │              │
│         └────────────────┼────────────────┼────────────────┘              │
│                          ↓                ↓                                │
│              ┌───────────────────────────────┐                             │
│              │      UI State Manager        │                             │
│              │   (VideoContext + Hooks)      │                             │
│              └───────────────────────────────┘                             │
│                          ↓                                                  │
│              ┌───────────────────────────────┐                             │
│              │      API Communication        │                             │
│              │   (REST + SSE EventSource)    │                             │
│              └───────────────┬───────────────┘                             │
└──────────────────────────────┼────────────────────────────────────────────┘
                               │ HTTP/WebSocket
                               ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SERVER LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        FastAPI Application                           │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │   │
│  │  │  Upload API   │  │  Frame API    │  │  OCR API      │           │   │
│  │  │  /upload      │  │  /frames/{id} │  │  /process     │           │   │
│  │  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘           │   │
│  │          │                  │                │                    │   │
│  │  ┌───────┴──────────────────┴────────────────┴───────┐             │   │
│  │  │              Service Layer                         │             │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│             │   │
│  │  │  │VideoService │  │FrameService │  │OCRService   ││             │   │
│  │  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘│             │   │
│  │  └─────────┼────────────────┼────────────────┼──────┘             │   │
│  │            │                │                │                     │   │
│  │  ┌─────────┴────────────────┴────────────────┴──────┐             │   │
│  │  │              Processing Workers (ThreadPool)        │             │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │             │   │
│  │  │  │ Video   │  │ Frame   │  │  OCR    │            │             │   │
│  │  │  │ Decoder │  │ Extract │  │ Engine  │            │             │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘            │             │   │
│  │  └───────────────────────────────────────────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                          ↓                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Storage Layer                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │   Upload    │  │   Frame     │  │   Results   │                 │   │
│  │  │  Directory  │  │   Cache     │  │  Database   │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation | VideoOCR Studio Mapping |
|-----------|----------------|------------------------|------------------------|
| **Upload Handler** | Receive video file, validate format, initiate processing | Multipart upload with chunked transfer | `POST /upload` endpoint |
| **Video Service** | Coordinate video operations, manage session state | Singleton service with dependency injection | Session management, job queue |
| **Frame Extractor** | Decode video, extract specific frames | FFmpeg/PyAV binding with seek optimization | Extract frames at timestamps |
| **OCR Engine** | Perform text recognition on frames | Tesseract/PaddleOCR wrapper | `POST /process` with selected frames |
| **Progress Tracker** | Emit SSE events for long operations | Async generator with queue | SSE endpoint `/progress/{job_id}` |
| **State Manager** | Manage frontend reactive state | React context / Vuex / vanilla state | VideoContext with useReducer |
| **Timeline Scrubber** | Render video preview, seek to timestamps | HTML5 Video element with canvas overlay | Custom React component |
| **Deduplication Engine** | Remove duplicate OCR results | Hash-based clustering | Backend service with similarity threshold |

## Recommended Project Structure

```
VideoOCR-Studio/
├── frontend/                      # HTML/CSS/JS single-page application
│   ├── index.html                 # Main entry point
│   ├── styles/
│   │   ├── main.css               # Core styles
│   │   ├── upload.css             # Upload widget styles
│   │   ├── timeline.css           # Scrubber and preview styles
│   │   └── output.css             # Results display styles
│   ├── js/
│   │   ├── app.js                 # Main application initialization
│   │   ├── api.js                 # REST API + SSE client
│   │   ├── state.js               # Central state management
│   │   ├── components/
│   │   │   ├── upload.js          # File upload widget
│   │   │   ├── video-player.js    # Video preview with canvas overlay
│   │   │   ├── timeline.js        # Timeline scrubber component
│   │   │   ├── frame-selector.js  # Frame selection interface
│   │   │   ├── progress.js        # Progress display component
│   │   │   └── output.js          # OCR results display
│   │   └── utils/
│   │       ├── formatters.js      # Text and time formatting
│   │       └── validators.js      # Input validation
│   └── assets/
│       └── icons/                 # UI icon assets
│
├── backend/                       # Python FastAPI application
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration management
│   ├── api/
│   │   ├── routes/
│   │   │   ├── upload.py          # Upload endpoints
│   │   │   ├── frames.py          # Frame retrieval endpoints
│   │   │   ├── ocr.py             # OCR processing endpoints
│   │   │   └── progress.py        # SSE progress endpoints
│   │   └── deps.py                # Dependency injection
│   ├── services/
│   │   ├── video_service.py       # Video operations coordinator
│   │   ├── frame_service.py       # Frame extraction logic
│   │   ├── ocr_service.py         # OCR processing logic
│   │   └── dedup_service.py       # Result deduplication
│   ├── workers/
│   │   ├── frame_extractor.py    # FFmpeg wrapper for frame extraction
│   │   ├── ocr_engine.py          # Tesseract/PaddleOCR interface
│   │   └── job_queue.py           # Background job management
│   ├── models/
│   │   ├── schemas.py             # Pydantic request/response models
│   │   └── database.py            # Database models (SQLite)
│   ├── storage/
│   │   ├── file_storage.py        # File system operations
│   │   └── cache_manager.py       # Frame cache management
│   └── utils/
│       ├── validators.py          # Input validation utilities
│       └── formatters.py          # Output formatting
│
├── tests/                         # Test suite
│   ├── frontend/                  # Frontend unit tests
│   └── backend/                   # Backend unit/integration tests
│
├── static_uploads/                # Uploaded video storage (gitignored)
├── extracted_frames/              # Cached frame images (gitignored)
├── results.db                     # SQLite database (gitignored)
├── requirements.txt               # Python dependencies
├── package.json                   # Frontend dependencies
└── README.md
```

### Structure Rationale

- **`frontend/`:** Self-contained static HTML/CSS/JS that can be served by FastAPI static file serving or nginx. No build step required initially.
- **`backend/api/routes/`:** Routes separated by domain (upload, frames, ocr, progress) for easy routing and testing.
- **`backend/services/`:** Business logic separated from HTTP handling. Services are testable without network layer.
- **`backend/workers/`:** CPU-intensive operations isolated from request handling. Allows graceful handling of timeouts.
- **`backend/storage/`:** File operations abstracted for easy migration to cloud storage later.
- **`static_uploads/` and `extracted_frames/`:** Separated to allow independent cleanup and cache management.

## Architectural Patterns

### Pattern 1: Service Layer Pattern

**What:** Business logic separated from HTTP request handlers.
**When to use:** Always. Prevents route handlers from becoming bloated.
**Trade-offs:** Adds indirection but improves testability.

```python
# routes/upload.py (thin handler)
@router.post("/upload")
async def upload_video(file: UploadFile, service: VideoService = Depends(get_video_service)):
    return await service.handle_upload(file)

# services/video_service.py (business logic)
class VideoService:
    def __init__(self, storage: FileStorage, db: Database):
        self.storage = storage
        self.db = db

    async def handle_upload(self, file: UploadFile) -> dict:
        # Validate, store, create session
        session_id = await self.storage.save_upload(file)
        await self.db.create_session(session_id)
        return {"session_id": session_id, "status": "ready"}
```

### Pattern 2: Server-Sent Events for Progress Updates

**What:** Unidirectional streaming from server to client for long-running operations.
**When to use:** Video processing, OCR on multiple frames, any operation taking more than 2 seconds.
**Trade-offs:** Simple, HTTP-based, no WebSocket complexity. Unidirectional only.

```python
# routes/progress.py
@router.get("/progress/{job_id}")
async def stream_progress(job_id: str):
    async def event_generator():
        pubsub = redis.pubsub() if using_redis else in_memory_broadcast
        await pubsub.subscribe(f"job:{job_id}")

        while True:
            message = await pubsub.get()
            if message is None:
                break
            yield f"data: {message}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

```javascript
// Frontend SSE client
const eventSource = new EventSource(`/progress/${jobId}`);
eventSource.onmessage = (event) => {
    const progress = JSON.parse(event.data);
    updateProgressBar(progress.percent);
    updateStatus(progress.status);
};
eventSource.onerror = () => {
    eventSource.close();
    handleConnectionError();
};
```

### Pattern 3: Job Queue with Background Workers

**What:** Long operations queued and processed asynchronously.
**When to use:** Frame extraction, OCR on multiple frames, any operation that could exceed HTTP timeout.
**Trade-offs:** Adds complexity (queue, workers) but improves responsiveness.

```python
# workers/job_queue.py
class JobQueue:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: dict[str, Job] = {}

    def submit(self, job_id: str, func, *args):
        future = self.executor.submit(func, *args)
        self.jobs[job_id] = {"future": future, "status": "running"}
        return job_id

    def get_status(self, job_id: str) -> dict:
        job = self.jobs.get(job_id)
        if not job:
            return {"status": "not_found"}
        future = job["future"]
        return {
            "status": "running" if not future.done() else "complete",
            "result": future.result() if future.done() else None
        }
```

### Pattern 4: Session-Based State Management

**What:** Server maintains processing session; client references session ID.
**When to use:** Multi-step workflows like VideoOCR (upload -> select frames -> process -> view results).
**Trade-offs:** Server stores state (memory/database), client is stateless regarding backend.

```python
# models/database.py
class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    video_path = Column(String)
    status = Column(String)  # "uploaded", "frames_extracted", "processing", "complete"
    created_at = Column(DateTime, default=datetime.utcnow)
    results = relationship("OCRResult", back_populates="session")

# API flow
# 1. POST /upload -> returns {session_id: "abc123"}
# 2. GET /frames?session_id=abc123 -> returns frame list
# 3. POST /process {session_id: "abc123", frame_indices: [0, 5, 10]}
# 4. GET /results?session_id=abc123 -> returns OCR text
```

## Data Flow

### Request Flow

```
[User drops video file]
         ↓
[Upload Widget] → [Validate file type/size]
         ↓ (valid)
[API Client] → POST /upload (multipart)
         ↓
[FastAPI Upload Handler] → [VideoService.handle_upload()]
         ↓
[FileStorage.save_upload()] → Write to static_uploads/
         ↓
[Database.create_session()] → Create session record
         ↓
[Return session_id to client]
         ↓
[Video Player requests video URL]
         ↓
[Static file served to <video> element]
```

### Frame Selection and Processing Flow

```
[User scrubs timeline]
         ↓
[Video Player] → Seek video to timestamp
         ↓
[User clicks "Select Frame"]
         ↓
[Frame Selector] → [Add frame to selection list]
         ↓
[User clicks "Extract Text" with selected frames]
         ↓
[API Client] → POST /process {session_id, frames: [{index, timestamp}]}
         ↓
[SSE connection opened to /progress/{session_id}]
         ↓
[FastAPI OCR Handler] → [JobQueue.submit()]
         ↓
[FrameExtractor] → FFmpeg extracts frames at timestamps
         ↓
[OCREngine] → PaddleOCR/Tesseract processes each frame
         ↓
[DeduplicationService] → Remove duplicate results
         ↓
[Store results in database]
         ↓
[SSE emits progress events] → [Frontend updates progress bar]
         ↓
[Job complete] → [SSE closes, client shows results]
```

### State Management

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend State (VideoContext)             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ session_id: string | null                            │   │
│  │ video_url: string | null                             │   │
│  │ selected_frames: Frame[]                            │   │
│  │ processing_status: "idle" | "processing" | "done"  │   │
│  │ progress_percent: number                             │   │
│  │ results: OCRResult[]                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓ (dispatch actions)            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Reducer (handleAction)                  │   │
│  │  SET_VIDEO → update video_url, session_id            │   │
│  │  SELECT_FRAME → add to selected_frames              │   │
│  │  REMOVE_FRAME → remove from selected_frames         │   │
│  │  START_PROCESSING → set status to "processing"      │   │
│  │  UPDATE_PROGRESS → update progress_percent          │   │
│  │  SET_RESULTS → store OCR results                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Components subscribe                 │   │
│  │  [Upload] [VideoPlayer] [Timeline] [Output]         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         ↓ (on user action)
[API calls to backend]
```

### Key Data Flows

1. **Video Upload Flow:** File dropped -> validated -> POST /upload -> saved to disk -> session created in DB -> session_id returned -> frontend loads video from static URL.

2. **Frame Selection Flow:** User scrubs video -> clicks to select -> frame added to selected_frames array in state -> user sees thumbnail of selections.

3. **OCR Processing Flow:** User triggers processing -> POST /process -> SSE opened -> backend extracts frames -> OCR runs -> deduplication -> results stored -> SSE sends completion -> frontend renders results.

4. **Progress Streaming Flow:** Backend processes frames -> emits SSE events with {frame: n, total: m, status: "processing"} -> frontend updates progress bar in real-time.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|-------------------------|
| 0-10 concurrent users | Current architecture is fine. SQLite, single-threaded OCR, local file storage. |
| 10-50 concurrent users | Add Redis for job queue (avoid memory leaks), consider moving to PostgreSQL. Serve static files from nginx instead of FastAPI. |
| 50-200 concurrent users | Horizontal scaling: multiple FastAPI workers behind load balancer. GPU instance for OCR. CDN for static files. |

### Scaling Priorities

1. **First bottleneck:** Frame extraction is CPU-bound. Use multiprocessing or offload to separate worker service.
2. **Second bottleneck:** File I/O on extracted frames. Consider memory-mapped files or streaming frames directly to OCR without disk caching.
3. **Third bottleneck:** SQLite under concurrent writes. Migrate to PostgreSQL with connection pooling.

## Anti-Patterns

### Anti-Pattern 1: Processing in HTTP Request Handler

**What people do:** Perform video decoding and OCR directly in route handlers, returning when complete.
**Why it's wrong:** HTTP request times out (usually 30-60 seconds), user gets no feedback, server blocks on slow operations.
**Do this instead:** Use job queue + SSE. Return 202 Accepted immediately, process in background, stream progress.

```python
# BAD
@router.post("/process")
async def process_video(frames: list[Frame], db: Session):
    results = []
    for frame in frames:
        img = extract_frame(frame.timestamp)  # Slow!
        text = ocr_engine.recognize(img)      # Slow!
        results.append(text)
    return {"results": results}

# GOOD
@router.post("/process")
async def start_processing(frames: list[Frame], service: OCRService):
    job_id = service.queue_job(frames)  # Immediate return
    return {"job_id": job_id, "status": "queued"}
```

### Anti-Pattern 2: Storing Large Files in Database

**What people do:** Store video bytes in BLOB columns or base64-encoded in text fields.
**Why it's wrong:** Database bloat, slow reads/writes, backup issues, no streaming support.
**Do this instead:** Store videos on file system (or S3-like storage), store paths/references in database.

### Anti-Pattern 3: Monolithic Frontend State

**What people do:** One massive JavaScript object for all application state, passed everywhere.
**Why it's wrong:** Unclear data flow, difficult to debug, components couple to global state.
**Do this instead:** Use component-level state + context provider for shared state (session info, progress). Keep components self-contained.

### Anti-Pattern 4: Tight Coupling Between Services

**What people do:** Services import each other directly, creating circular dependencies and difficult testing.
**Why it's wrong:** Changes in one service break others, testing requires full stack.
**Do this instead:** Use dependency injection, pass interfaces not implementations. Services depend on abstractions.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Tesseract OCR | Python bindings via pytesseract or tesseract-ocr | Must be installed on system. Alternative: PaddleOCR (pure Python, GPU support) |
| FFmpeg | Python wrapper via ffmpeg-python or subprocess | Must be installed on system. Core video processing tool. |
| SQLite | SQLAlchemy ORM | Simple, no separate server. Fine for single-instance. |
| PostgreSQL | asyncpg or SQLAlchemy async | Use when scaling beyond 10 concurrent users. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend ↔ Backend | REST API (JSON) + SSE | Clear contract, versioned endpoints |
| Route Handler ↔ Service | Direct function call (Python dependency injection) | Fast, testable |
| Service ↔ Worker | ThreadPoolExecutor.submit() or separate process | Isolate CPU-bound work |
| Service ↔ Storage | File I/O + SQLAlchemy queries | Abstract behind service methods for future migration |
| Backend ↔ Database | SQLAlchemy ORM | Async for better concurrency |

## Build Order Implications

Based on the architecture, recommended build sequence:

### Phase 1: Backend Core (Services and Routes)
1. **File storage service** - foundation for everything
2. **Database models and session management** - track state across requests
3. **Upload endpoint** - first user interaction point

### Phase 2: Video Playback (Frontend)
4. **Static file serving** - serve uploaded videos
5. **Video player component** - display video, basic scrubbing
6. **Upload widget** - dropzone for file selection

### Phase 3: Frame Selection (Frontend)
7. **Timeline scrubber** - visual timeline with seek capability
8. **Frame selector** - capture frames at timestamps
9. **Selection management UI** - view/remove selected frames

### Phase 4: OCR Pipeline (Backend)
10. **Frame extraction worker** - FFmpeg integration
11. **OCR engine integration** - Tesseract or PaddleOCR
12. **Deduplication service** - remove duplicate results

### Phase 5: Processing Flow (Frontend + Backend)
13. **Process endpoint with job queue** - background processing
14. **SSE progress streaming** - real-time updates
15. **Progress display component** - visual feedback

### Phase 6: Output and Polish (Frontend)
16. **Results display** - formatted OCR text with timestamps
17. **Export functionality** - download results as text/JSON
18. **Validation and error handling** - edge cases

### Dependency Graph

```
Phase 1 (Backend Core)
    ├── file_storage (no dependencies)
    ├── session_db (no dependencies)
    └── upload_endpoint (depends on file_storage + session_db)
            ↓
Phase 2 (Video Playback) requires Phase 1
    ├── static_serving (depends on upload completing)
    ├── video_player (depends on static_serving)
    └── upload_widget (depends on upload_endpoint)
            ↓
Phase 3 (Frame Selection) requires Phase 2
    ├── timeline_scrubber (depends on video_player)
    ├── frame_selector (depends on timeline_scrubber)
    └── selection_ui (depends on frame_selector)
            ↓
Phase 4 (OCR Pipeline) requires Phase 1
    ├── frame_extractor (depends on session_db)
    ├── ocr_engine (depends on frame_extractor)
    └── deduplication (depends on ocr_engine)
            ↓
Phase 5 (Processing Flow) requires Phase 3 + Phase 4
    ├── job_queue (depends on ocr_pipeline)
    ├── sse_progress (depends on job_queue)
    └── progress_display (depends on sse_progress)
            ↓
Phase 6 (Output) requires Phase 5
    ├── results_display (depends on job_queue completion)
    ├── export (depends on results_display)
    └── validation (spans all phases)
```

## Sources

- FastAPI documentation on streaming responses and background tasks: https://fastapi.tiangolo.com
- SSE specification: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
- FFmpeg Python bindings: https://github.com/kkroening/ffmpeg-python
- PaddleOCR documentation: https://github.com/PaddlePaddle/PaddleOCR
- Service layer pattern: Clean Architecture principles (Robert C. Martin)
- Tesseract documentation: https://github.com/tesseract-ocr/tesseract

---

*Architecture research for: VideoOCR Studio*
*Researched: 2026-04-22*