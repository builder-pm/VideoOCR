---
status: draft
phase: 02
name: Frontend Core
---

# UI Specification - Phase 02: Frontend Core

## 1. Visual Identity

### Spacing
- **Base Unit:** 4px
- **Scale:** 4, 8, 16, 24, 32, 48, 64
- **Touch Targets:** 44px minimum for all interactive handles and buttons.
- **Exceptions:** Timeline handles may have a 12px visual width but must have a 44px invisible hit area.

### Typography
- **Primary UI Font:** `Satoshi`, sans-serif (via Fontshare)
- **Code/Monospace Font:** `JetBrains Mono`, monospace (via CDN)
- **Sizes:**
  - `H1`: 28px / 1.2 line-height / Weight 600
  - `H2`: 20px / 1.2 line-height / Weight 600
  - `Body`: 16px / 1.5 line-height / Weight 400
  - `Caption`: 14px / 1.4 line-height / Weight 400
- **Weights:** Regular (400), Semibold (600)

### Color Palette
- **Dominant Surface (60%):** `#0f0e0c` (App background, deep dark)
- **Secondary Surface (30%):** `#141312` (Sidebar, cards, control panels)
- **Accent Color (10%):** `#01696f` (Primary buttons, active slider tracks, timeline handles)
- **Text (Primary):** `#ffffff` (Headings, active text)
- **Text (Secondary):** `#a1a1a1` (Labels, captions, disabled text)
- **Status - Warning:** `#f59e0b` (Frame count warnings)
- **Status - Success:** `#10b981` (Completed states)
- **Status - Destructive:** `#ef4444` (Clear/Reset actions)

## 2. Component Inventory

### Upload Panel
- **State: Empty:**
  - Large dashed border dropzone.
  - Icon: Upload cloud/arrow.
  - Copy: "Drag and drop video here or click to browse"
  - Subtext: "Supported: MP4, MOV, AVI, WEBM (Max 2GB)"
- **State: Loading:**
  - Spinner with "Uploading..." text.
- **State: Ready:**
  - Mini thumbnail of video.
  - Filename and size metadata display.

### Video Preview & Metadata
- **Layout:** Centered video player or thumbnail.
- **Metadata Badges:**
  - Duration: `00:00:00`
  - Resolution: `1920x1080`
  - Native FPS: `30 fps`

### Timeline Scrubber
- **Track:** Full width of the content area.
- **Handles:** Two draggable teal handles for `START` and `END`.
- **Timecodes:** Real-time `MM:SS` display floating above handles.
- **Preview Tooltip:** Small thumbnail showing frame at current scrubber position.
- **Quick Presets:** Small pill buttons below timeline.
  - Labels: "First 2 min", "First 5 min", "Full video"

### Configuration Controls
- **Frame Rate Slider:**
  - Range: 0.5 to 30.
  - Stops: 0.5, 1, 2, 5, 10, 15, 30.
  - Real-time Stats: "Estimated: {N} frames | ~{M} min processing"
  - Warning: Amber badge appears if frames > 5000.
- **Advanced Options (Collapsible):**
  - **Blur Threshold Slider:** 0 to 300 (Default: 100).
  - **OCR Engine Toggle:** Segmented control [PaddleOCR | Tesseract].
  - **Deduplication Toggle:** Switch/Checkbox (Default: ON).
  - **Language Selector:** Dropdown [English, Hindi, English+Hindi].

## 3. Interaction Contract

### Behaviors
- **Drag-and-Drop:** Visual feedback (border color change to accent) when file is hovered over dropzone.
- **Timeline Scrubbing:** Video element seeks in sync with handle movement.
- **Collapsible Panels:** Advanced options defaults to closed; expands with smooth transition.
- **Validation:** "Extract Text" button (Phase 3) remains disabled until valid video is uploaded.

### Error/Warning States
- **Invalid Format:** Toast or inline alert: "Unsupported file type."
- **High Frame Count:** Warning icon next to estimated frame count when > 5000.
- **File Size:** Inline warning: "Large file detected (>2GB). Processing may be slow."

## 4. Copywriting

| Element | Copy |
|---------|------|
| Primary Upload CTA | "Select Video to Process" |
| Dropzone Hover | "Drop video to start" |
| Empty State | "No video selected. Upload a file to configure extraction." |
| Preset 1 | "First 2 Minutes" |
| Preset 2 | "First 5 Minutes" |
| Preset 3 | "Full Duration" |
| Frame Count Warning | "High frame count may result in long processing times." |
| Advanced Header | "Advanced Extraction Settings" |

## 5. Registry Safety Gate

| Tool | Registry | Safety Gate |
|------|----------|-------------|
| None | Vanilla HTML/CSS/JS | No third-party registries used. All components custom-built. |

---
*UI-SPEC Generated: 2026-04-22*
*Source: REQUIREMENTS.md, PROJECT.md, CLAUDE.md*
