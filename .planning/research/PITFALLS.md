# Pitfalls Research

**Domain:** Video OCR Desktop Application
**Researched:** 2026-04-22
**Confidence:** MEDIUM

Based on research across OCR tooling, video processing patterns, and desktop application pitfalls.

## Critical Pitfalls

### Pitfall 1: Ignoring Frame Quality Before OCR

**What goes wrong:**
OCR runs on every extracted frame regardless of quality, producing garbage text from blurry, low-resolution, or motion-contaminated frames. The output looks like a transcript but contains mostly false positives and unreadable garbage.

**Why it happens:**
Developers focus on "extracting text" not "extracting readable text." FFmpeg extracts frames at default settings, which may be sub-540p, highly compressed, or captured at motion moments. Tesseract/PaddleOCR then processes this degraded input and produces garbage confidence scores and wrong characters.

**How to avoid:**
1. Implement pre-OCR quality gate: blur detection (Laplacian variance < threshold), resolution check (< minimum pixels), contrast ratio check
2. Reject frames that fail quality gates BEFORE sending to OCR engine
3. Log which frames were rejected and why -- this informs frame rate selection
4. Use FFmpeg scaling to upsample low-resolution frames before OCR (e.g., `scale=1920:1080:flags=lanczos`)

**Warning signs:**
- OCR output contains many single characters, symbols, or random noise
- Confidence scores from OCR engine are consistently low (< 0.6)
- Timestamps in output don't match visible text in video
- Processing completes quickly (indicates too many frames skipped/rejected by broken logic)

**Phase to address:**
Phase 2 (Frame Extraction & Quality) -- quality gates must be built into the extraction pipeline, not added as a post-processing step.

---

### Pitfall 2: No Frame Deduplication Strategy

**What goes wrong:**
Video typically has 24-60 frames per second. Most consecutive frames contain identical or near-identical text (e.g., a static lower-third graphic). Processing all of them wastes 80-95% of compute on duplicate work, dramatically slowing results and inflating output with redundant entries.

**Why it happens:**
Developers either:
- Process every Nth frame (e.g., every 30th frame) without checking if content changed
- Use fixed frame intervals regardless of scene changes
- Don't compare extracted frames to detect when text actually changes

**How to avoid:**
1. Implement frame-to-frame comparison using perceptual hashing (pHash) or structural similarity (SSIM)
2. Only run OCR on frames that differ from the previous processed frame by more than a threshold (e.g., pHash hamming distance > 10)
3. Consider scene change detection via histogram comparison as a faster but less accurate alternative
4. Deduplication threshold should be configurable -- different content types need different sensitivity

**Warning signs:**
- Processing time scales linearly with video duration even for static text content
- Output contains long runs of identical text with different timestamps
- User reports "it takes forever" for short videos with lots of static overlays

**Phase to address:**
Phase 2 (Frame Extraction & Quality) -- deduplication must integrate with extraction, not be a post-processing filter.

---

### Pitfall 3: Memory Exhaustion With Large Videos

**What goes wrong:**
Loading large video files (2GB+) into memory, storing all extracted frames as full-resolution images, or running multiple OCR instances simultaneously causes OOM (Out of Memory) kills, crashing the Python backend or freezing the system.

**Why it happens:**
- `cv2.VideoCapture` can buffer multiple frames
- Storing extracted frames in a list consumes RAM proportional to video length
- OCR engines (especially PaddleOCR with its ML models) consume significant memory per instance
- No streaming/chunking strategy for processing

**How to avoid:**
1. Process frames in bounded chunks (e.g., never hold more than N frames in memory at once)
2. Release `cv2.VideoCapture` objects immediately after frame extraction
3. Run OCR in a single-threaded queue with bounded concurrency (max 1-2 parallel OCR tasks)
4. For very large videos, consider segment-based processing with intermediate saves to disk
5. Set memory budgets and add explicit cleanup (explicit `del` + `gc.collect()` after processing batches)

**Warning signs:**
- Process memory grows continuously during processing
- Swap file usage increases on long-running operations
- FastAPI crashes with no error message or OOM in logs
- Browser becomes unresponsive while waiting for response (backend blocked)

**Phase to address:**
Phase 1 (Backend Foundation) -- streaming architecture and memory management must be foundational, not retrofitted.

---

### Pitfall 4: FFmpeg Integration Fragility

**What goes wrong:**
FFmpeg commands fail silently, produce empty output, or have codec compatibility issues that are hard to diagnose. The application appears to hang or returns no results with no explanation of why.

**Why it happens:**
- FFmpeg is called via subprocess with limited error capture
- Codecs not installed on target system (e.g., H.265/HEVC, specific container formats)
- Frame extraction produces 0-frame outputs without raising errors
- Path handling differences between FFmpeg CLI and Python (spaces, unicode, backslashes)

**How to avoid:**
1. Always capture both stdout AND stderr from FFmpeg subprocess
2. Check return codes explicitly -- non-zero means failure
3. Test with common codec/container combinations explicitly
4. Provide informative errors: "FFmpeg failed: [stderr]" not just "processing failed"
5. Consider using ffprobe to validate video before processing (check duration, codec, resolution)
6. Wrap FFmpeg calls in a dedicated module with retry logic and clear error messages

**Warning signs:**
- Silent failures where output file is empty (0 bytes)
- FFmpeg produces different results on different machines (codec availability)
- Errors only appear in terminal, not in application logs
- "Works on my machine" reports from users

**Phase to address:**
Phase 1 (Backend Foundation) -- FFmpeg integration layer must handle errors gracefully with informative feedback.

---

### Pitfall 5: SSE Progress Updates Stop Working

**What goes wrong:**
The frontend shows "Processing..." forever because SSE progress stream disconnects, stalls, or gets blocked. User doesn't know if the process is stuck, failed, or still running.

**Why it happens:**
- FastAPI background task dies silently (exception without handler)
- SSE connection drops on backend restart or timeout
- Progress events not flushed to buffer (buffering in production ASGI server)
- Server closes connection when HTTP request times out but task is still running

**How to avoid:**
1. Implement SSE heartbeat/ping every 5-10 seconds to detect dead connections
2. Track background task state in Redis or in-memory dict; expose a status endpoint
3. Flush SSE buffer on each write (depends on ASGI server config)
4. Use async iteration pattern for SSE: `async def event_generator()` with proper cancellation handling
5. Include "processing complete" or "processing failed" terminal event

**Warning signs:**
- Frontend progress bar freezes at 80-90% (output nearly done but SSE stalled)
- SSE connection closes before final results arrive
- Backend logs show task completed but frontend never received completion event
- "Connection reset by peer" errors in browser console

**Phase to address:**
Phase 3 (Processing Pipeline) -- SSE must be tested end-to-end including failure scenarios.

---

### Pitfall 6: OCR Accuracy Without Context

**What goes wrong:**
OCR produces text that is technically accurate per-character but meaningless in context (e.g., "8:00PM" vs "8:00 PM", wrong hyphenation, missing spaces between words, merged words from low-resolution). User gets raw OCR output that requires significant manual cleanup.

**Why it happens:**
- OCR engines are optimized for document scanning, not video overlays
- Video text often has: low resolution, anti-aliasing artifacts, colored text on complex backgrounds, non-standard fonts
- No post-processing to fix common OCR errors (character substitution, spacing)

**How to avoid:**
1. Configure OCR engine for "sparse text" mode (Tesseract config `--psm 11` or PaddleOCR `doc_analysis_ocr`):
   - Tesseract: `--oem 3 --psm 11` for sparse
   - PaddleOCR: enable `text_detect=False` for known text regions
2. Implement post-processing rules: fix common substitutions (0/O, 1/l/I), normalize spacing, fix common phrase patterns
3. Consider adding a confidence filter: discard results below threshold (e.g., < 0.5 confidence) and flag them
4. Display confidence scores in UI so users know which results are uncertain

**Warning signs:**
- OCR output contains obvious wrong characters in otherwise correct words (e.g., "M1llion" instead of "Million")
- User feedback: "90% of the text is wrong"
- Output passes character-level accuracy checks but fails word-level checks

**Phase to address:**
Phase 2 (Frame Extraction & Quality) -- OCR configuration and post-processing must be part of the core pipeline.

---

### Pitfall 7: Hardcoded Paths and Environment Assumptions

**What goes wrong:**
Application works on developer's machine but fails on user's machine due to hardcoded FFmpeg paths, missing system libraries, or environment-specific assumptions. Installation is a nightmare.

**Why it happens:**
- `ffmpeg` assumed to be in PATH (user installed it elsewhere)
- Working directory assumed to be project root
- Temp folder paths hardcoded as `/tmp/` which doesn't exist on Windows
- Assumption that specific codecs are installed

**How to avoid:**
1. Make FFmpeg path configurable via environment variable or config file
2. Use `shutil.which("ffmpeg")` to find FFmpeg in PATH as fallback
3. Use `tempfile` module for all temp files (handles cross-platform)
4. Detect OS and use appropriate paths (Windows: `%APPDATA%`, Linux: `/tmp`, macOS: `/tmp`)
5. Bundle FFmpeg with application (e.g., via pyinstaller) OR provide clear installation instructions
6. On startup, validate all required binaries exist and report missing ones clearly

**Warning signs:**
- "FFmpeg not found" errors on fresh install
- Different behavior on Windows vs Linux
- Temp file creation fails silently
- "Works on my machine" reports

**Phase to address:**
Phase 1 (Backend Foundation) -- environment validation and cross-platform path handling must be foundational.

---

### Pitfall 8: No Incremental/Resume Capability

**What goes wrong:**
Processing a 2-hour video takes 45 minutes. User's computer goes to sleep at minute 40. All progress is lost. User must restart from scratch.

**Why it happens:**
- No checkpointing of processing state
- No intermediate saves to disk
- No way to resume from last completed frame
- Temporary files cleaned up on restart

**How to avoid:**
1. Implement checkpointing: save processed frame index and intermediate results after each frame or batch
2. On restart, check for existing checkpoint and resume from there
3. Store results incrementally (append to output file as each frame completes)
4. Use a job database (SQLite) to track processing state: job_id, video_path, last_processed_frame, status

**Warning signs:**
- Users report losing progress when application closes unexpectedly
- Long processing times with no way to check partial progress
- No "pause" functionality

**Phase to address:**
Phase 3 (Processing Pipeline) -- checkpointing is part of robust pipeline design.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Process all frames (no deduplication) | Simpler code | 5-10x slower processing, bloated output | Never for production |
| Single-threaded processing | No concurrency bugs | Very slow for multi-core machines | MVP only |
| Hardcode FFmpeg path | Works on dev machine | Fails on all user machines | Never |
| Skip error handling for FFmpeg | Faster to implement | Silent failures, no debugging | Never |
| No progress feedback | Simpler SSE code | User thinks app is stuck | Never |
| Store all frames in memory | Faster access | OOM on large videos | Never |
| Use default Tesseract PSM | Works for some content | Poor accuracy on sparse video text | Never |
| Skip frame quality check | Fewer code paths | Garbage OCR output | Never |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| FFmpeg subprocess | Not capturing stderr, missing errors | Capture stdout + stderr, log return code |
| FFmpeg codec | Assuming H.264 always available | Validate codec availability, provide fallback |
| OpenCV VideoCapture | Not releasing object after use | Use context manager or explicit release |
| Tesseract | Using default config for video text | Use `--psm 11` (sparse) and `--oem 3` |
| PaddleOCR | Using default model for low-res frames | Use specific detection model, enable angle classification |
| SSE | Not handling client disconnect | Catch `CancelledError` in async generator |
| SSE | Blocking writes slow down backend | Use non-blocking send pattern with queue |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| In-memory frame buffer | Memory grows with video length | Use chunked processing with disk spillover | Videos > 30 min at high resolution |
| Multiple parallel OCR instances | CPU saturation, OOM crashes | Limit concurrency to 1-2 instances | Always on consumer hardware |
| Unoptimized FFmpeg frame extraction | Frame extraction is the bottleneck | Use `-q:v 2` for quality, direct RGB output | Always |
| No deduplication | Processing time proportional to frame count | Perceptual hash comparison before OCR | All real-world videos |
| Large video upload to memory | Browser and server both crash | Stream upload directly to disk, don't buffer in RAM | Videos > 500MB |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Storing uploaded video with predictable filename | Path traversal, file overwrite | Use UUID filenames, store in app-specific temp directory |
| No file size limit on upload | DoS by uploading massive files | Enforce max file size (e.g., 4GB) at upload, not just processing |
| Temp files not cleaned up | Disk space exhaustion over time | Use `tempfile` with auto-cleanup, run cleanup job on startup |
| No virus scan on uploaded files | Malware introduction to processing pipeline | At minimum, use Python `python-magic` to validate file headers |
| FFmpeg command injection via filename | Shell injection if filenames aren't sanitized | Always escape/sanitize filenames passed to FFmpeg, use list args not shell |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No feedback during 30+ min processing | User thinks app is frozen, kills it | Real-time progress with ETA, percentage, current frame |
| Default frame rate too high (e.g., 1fps) | Misses fast-changing text | Show detected text density per frame, recommend optimal rate |
| Un-editable output | User cannot fix obvious OCR errors | Inline editable text with character-level confidence highlighting |
| No preview of extracted frames | User doesn't understand why text was missed | Show thumbnail of frames used for each text block |
| Processing fails with no explanation | User doesn't know what went wrong | Show which step failed, provide "retry" option with debug info |
| Timeline scrubber doesn't sync with text | Hard to find text by video position | Clicking text in output jumps to that frame in video |

## "Looks Done But Isn't" Checklist

- [ ] **Frame Extraction:** Tested with HEVC codec video? -- H.264 only works in dev
- [ ] **OCR Accuracy:** Tested with low-resolution video (720p or lower)? -- 1080p+ looks great, lower breaks
- [ ] **Progress Updates:** Tested with a 1-hour video? -- Short videos complete before SSE is even verified
- [ ] **Memory Handling:** Tested with a 2GB+ video file? -- Smaller files never trigger OOM
- [ ] **Error Handling:** Tested with a corrupted video file? -- Valid files always work, broken ones expose gaps
- [ ] **Path Handling:** Tested on Windows (different PATH separator, temp folder)? -- Linux paths work on Linux
- [ ] **Deduplication:** Tested with video that has static text overlays (news, talk shows)? -- Fast-cut videos have natural dedup
- [ ] **Output Editing:** Tested by editing extracted text? -- Output generation looks done, editing is never tested

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Frame extraction fails | LOW | Retry with different FFmpeg flags, validate codec first |
| OOM during processing | MEDIUM | Kill process, clear temp files, restart with lower resolution frames |
| SSE disconnects | LOW | Frontend auto-reconnects, backend queues last known progress |
| OCR produces garbage | MEDIUM | Adjust preprocessing (sharpen, upscale), tune confidence threshold |
| FFmpeg codec missing | LOW | Inform user which codec is missing, provide installation instructions |
| Video file corrupted | LOW | ffprobe validation before processing, clear error message |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Frame quality gates | Phase 2 (Frame Extraction) | Process blurry video, verify low-quality frames are skipped |
| Deduplication | Phase 2 (Frame Extraction) | Process static-overlay video, verify output has no duplicate entries |
| Memory management | Phase 1 (Backend Foundation) | Process 2GB+ video, monitor RAM stays bounded |
| FFmpeg integration | Phase 1 (Backend Foundation) | Test with H.265/HEVC video, verify error messages are informative |
| SSE progress updates | Phase 3 (Processing Pipeline) | Kill backend mid-processing, verify frontend reconnects and shows status |
| OCR accuracy | Phase 2 (Frame Extraction) | Process low-res video, spot-check character accuracy |
| Path handling | Phase 1 (Backend Foundation) | Test on Windows with spaces in username and path |
| Resume capability | Phase 3 (Processing Pipeline) | Kill process mid-run, restart, verify it resumes from checkpoint |

## Sources

- Tesseract documentation: PSM modes and OEM configuration for sparse text
- PaddleOCR GitHub issues: Common accuracy failures on low-resolution input
- FFmpeg documentation: Codec compatibility and frame extraction best practices
- OpenCV VideoCapture memory management documentation
- FastAPI SSE implementation patterns (official docs + community examples)
- Video OCR project post-mortems on GitHub and Stack Overflow
- Python asyncio patterns for background task management

---

*Pitfalls research for: VideoOCR Studio*
*Researched: 2026-04-22*