# Context: 02-frontend-core

**Goal:** Implement the core frontend for VideoOCR Studio using Vanilla HTML/CSS/JS.

## Phase Scope
- Single-page application (SPA) structure in `index.html` (served by FastAPI).
- Drag-and-drop upload interface.
- Video preview with timeline scrubbing and range selection (START/END handles).
- Processing configuration controls (FPS, Blur Threshold, OCR Engine, etc.).
- Real-time estimation of frames and processing time.

## Design Constraints
- Dark mode first (Dominant: #0f0e0c, Secondary: #141312, Accent: #01696f).
- Fonts: Satoshi (Sans), JetBrains Mono (Mono).
- No build step (use CDNs for fonts/icons if needed, otherwise local assets).

## Success Criteria
1. Drag-and-drop upload works.
2. Metadata displayed correctly.
3. Interactive timeline with draggable handles.
4. Presets (2m, 5m, full) work.
5. Slider for FPS (0.5-30) with stops.
6. Real-time frame/time estimation.
7. Advanced options panel (collapsible).

## Integration
- Communicates with existing FastAPI backend (`server.py`).
- Uses `/upload` and `/metadata` (if added) or extracts metadata client-side.
