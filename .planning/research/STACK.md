# Stack Research

**Domain:** Local Video OCR Application with Web UI
**Researched:** 2026-04-22
**Confidence:** MEDIUM-HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **FastAPI** | 0.128.0 | REST API backend | Standard for Python web APIs; native async support critical for long-running video processing; automatic OpenAPI docs; built-in validation reduces boilerplate. Verified from PyPI December 2025 release. |
| **uvicorn** | 0.32.x | ASGI server | Industry standard for FastAPI; handles concurrent requests well; supports reload for development. Version verified from PyPI. |
| **PaddleOCR** | 2.7.x / 3.x | Primary OCR engine | Best accuracy for rotated/mixed-orientation text common in scrolling videos; PP-OCRv4/v5 models provide significant accuracy gains over Tesseract; supports 80+ languages. GitHub v3.x released April 2026. |
| **pytesseract** | 0.3.x | Fallback OCR wrapper | Mature, stable; better for simple well-aligned text; no ML dependency overhead. Verified from PyPI August 2024. |
| **OpenCV** | 4.12.x | Video/frame processing | Industry standard for video processing; Laplacian blur detection is battle-tested; frame extraction reliable across codecs. Verified from PyPI July 2025. |
| **FFmpeg** | System-level | Video decoding | THE standard for video processing; must be installed separately; open-source, universal codec support. Do NOT use ffmpeg-python wrapper (v0.2.0, abandoned 2019) - use subprocess instead. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **python-multipart** | 0.0.x | File upload streaming | FastAPI file uploads; required for streaming video upload rather than buffered |
| **Pillow** | 12.0.x | Image processing | Frame preprocessing before OCR; resizing, format conversion |
| **numpy** | 2.3.x | Array operations | OpenCV arrays, frame data manipulation; use 2.3.x not 2.4.0 (yanked Dec 2025 due to backward compatibility bug) |
| **aiofiles** | 24.x | Async file I/O | Non-blocking file writes for frame extraction |
| **python-dotenv** | 1.x | Environment config | Local config without system-level env vars |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **Tesseract OCR** | System binary | Must be installed separately; Windows: use chocolatey or official installer; provides actual OCR engine for pytesseract wrapper |
| **FFmpeg binaries** | System binary | Must be installed separately; Windows: use chocolatey or official builds; add to PATH |
| **HTTPie** | API testing | Better than curl for debugging SSE streams |

## Installation

```bash
# System dependencies (must be pre-installed)
# Windows:
choco install tesseract ffmpeg

# Python dependencies
pip install fastapi==0.128.0
pip install uvicorn[standard]==0.32.0
pip install python-multipart==0.0.27
pip install paddleocr==2.9.1
pip install pytesseract==0.3.13
pip install opencv-python==4.12.0.90
pip install Pillow==12.0.0
pip install numpy==2.3.5
pip install aiofiles==24.1.0
pip install python-dotenv==1.0.1
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| PaddleOCR | EasyOCR | EasyOCR has simpler API but lower accuracy on rotated/mixed text; use only if PaddleOCR setup is problematic |
| PaddleOCR | TrOCR (Azure/Transformers) | TrOCR offers higher accuracy but requires cloud API or heavy local inference; overkill for scrolling document OCR |
| subprocess FFmpeg | ffmpeg-python | AVOID ffmpeg-python (abandoned 2019, v0.2.0); subprocess with proper command construction is more reliable |
| opencv-python | opencv-python-headless | Headless has issues with some OpenCV features; use full opencv-python for local desktop app |
| FastAPI | Flask | Flask requires more manual code for async/SSE; FastAPI's native support is worth the framework choice |
| FastAPI | Starlette directly | FastAPI adds validation, OpenAPI, dependency injection on top of Starlette; worth the thin abstraction |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **ffmpeg-python** | Abandoned library (v0.2.0, 2019); no maintenance; known bugs with complex filters | subprocess with f-strings or shlex |
| **numpy 2.4.0** | Yanked December 2025 due to backward compatibility bug | numpy 2.3.5 |
| **opencv-contrib-python** | Contains non-free algorithms with licensing ambiguity; larger package | opencv-python (standard) |
| **Celery/Redis** | Overkill for single-user local app; adds deployment complexity | FastAPI's native BackgroundTasks |
| **PaddleOCR latest (3.x)** | v3.5.0 (April 2026) requires PaddlePaddle 3.3+ which has heavy dependencies; v2.7.x is stable, well-documented | PaddleOCR 2.9.x (compatible with PaddlePaddle 2.x-3.x) |
| **WebSocket for progress** | SSE is simpler for one-way server-to-client progress; WebSocket adds complexity without benefit | SSE via FastAPI StreamingResponse |
| **cloud OCR services** | Violates local-only constraint; adds cost, privacy risk, network dependency | PaddleOCR + Tesseract (local processing) |

## Stack Patterns by Variant

**If GPU available (NVIDIA CUDA):**
- Use PaddlePaddle with CUDA support for faster OCR inference
- `pip install paddlepaddle-gpu`
- 3-5x speedup on OCR processing vs CPU

**If CPU-only (default):**
- Use PaddlePaddle CPU version (lighter weight)
- Focus optimization on frame extraction (FFmpeg) and blur filtering (OpenCV) rather than OCR speed

**If processing large videos (>2GB, >60min):**
- Implement chunked frame extraction (process in batches)
- Use opencv-python-headless for memory efficiency (no GUI overhead)
- Consider adding disk cache for intermediate frames

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| FastAPI 0.128.0 | uvicorn >= 0.23 | Use uvicorn[standard] for websocket support |
| PaddleOCR 2.9.x | PaddlePaddle >= 2.5.1, < 3.0 (for stability) | PaddlePaddle 3.x support varies; 2.x more stable |
| PaddleOCR 2.9.x | OpenCV >= 4.5, Python >= 3.8 | Standard dependencies |
| opencv-python 4.12.x | numpy >= 1.21, < 3.0 | numpy 2.x support added in 4.10+ |
| pytesseract 0.3.x | Pillow >= 8.0, Tesseract >= 4.1 | Tesseract 5.4 recommended |
| python-multipart 0.0.x | FastAPI >= 0.100.0 | Required for FastAPI file uploads |

## Key Architecture Decisions from Stack

1. **Subprocess over ffmpeg-python**: Direct FFmpeg invocation via `subprocess.run()` is more reliable and allows precise control over frame extraction parameters.

2. **SSE over WebSocket**: For progress streaming, Server-Sent Events (SSE) via `StreamingResponse` provides simpler implementation with less overhead than WebSocket.

3. **PaddleOCR primary, Tesseract fallback**: PaddleOCR handles challenging text (rotated, mixed scripts) better; Tesseract for simple, well-aligned text with lower resource usage.

4. **Async throughout**: Use `asyncpg` patterns (even without PostgreSQL) - async file handling, async OCR calls where possible, to prevent blocking the event loop during video processing.

5. **Background processing**: Use FastAPI `BackgroundTasks` for video processing - user gets immediate response with SSE progress channel, processing continues asynchronously.

---

*Stack research for: VideoOCR Studio (local video OCR with web UI)*
*Researched: 2026-04-22*
