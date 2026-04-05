# Hoard — User Guide

## Overview

Hoard is a web-based video file browser. It lets you navigate a network drive (NAS), play videos directly in the browser, and remember where you left off.

---

## Main Interface

The interface is split into two areas:

- **Left (or full-screen on mobile):** the file browser
- **Right (or full-screen overlay on mobile):** the video player

### File Browser

The browser displays the contents of a folder. A **breadcrumb** at the top lets you navigate up. The **🏠** button returns to the root.

Each file or folder is shown with:

- Its name
- A **watch status indicator** (for video files):
  - Neutral background → **unseen**
  - Yellow background + progress bar + percentage → **in progress**
  - Green background → **watched** (≥ 90 % viewed)

### File Actions

Hovering over a file (or long-pressing on mobile) reveals action buttons:

| Action | Description |
|--------|-------------|
| **▶ Play** | Opens the video in the player |
| **📁 Move** | Opens the quick-move modal (pinned folders) |
| **🗑 Delete** | Deletes the file after confirmation |

---

## Video Player

### Controls

| Element | Role |
|---------|------|
| **Progress bar** | Shows and controls position in the video |
| **⏮ / ⏭** | Seek back / forward 30 seconds |
| **◀◀ / ▶▶** | Seek back / forward 10 seconds |
| **▶ / ⏸** | Play / Pause |
| **🔊** | Mute/unmute |
| **Volume** | Volume slider |
| **⛶** | Fullscreen |

### Auto-resume

Position is saved automatically every 5 seconds. When you re-open a file, playback resumes from where you stopped.

### IN/OUT Markers (trim)

The `[IN` and `OUT]` buttons define a restricted playback zone (without modifying the file). The ✂ button triggers a physical file cut via ffmpeg.

---

## Touch Gestures

Gestures work directly on the video image.

### Single Tap

| Area | Action |
|------|--------|
| Centre (upper area) | Play / Pause |
| Centre (bottom strip) | Show / hide controls |

### Double Tap

| Area | Action |
|------|--------|
| Left edge (< 20 % width) | Seek back 30 s |
| Right edge — bottom third | Seek forward 30 s |
| Right edge — middle third | Seek forward 60 s |
| Right edge — top third | Seek forward 90 s |
| Centre | Fullscreen |

### Triple Tap

Toggle between **Fit** (full image visible) and **Fill** (cropped) display modes.

### Horizontal Swipe

Progressive seek through the video. **Speed depends on the vertical position of the finger**: a swipe at the top of the screen moves faster than at the bottom.

### Vertical Swipe

| Horizontal zone | Action |
|----------------|--------|
| Left edge (< 20 %) | Image brightness |
| Right edge (> 80 %) | Volume |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `←` | Seek back 10 s |
| `→` | Seek forward 10 s |
| `↑` | Volume + 10 % |
| `↓` | Volume − 10 % |
| `F` | Fullscreen |
| `M` | Mute |

---

## Quick Folders (Pins)

**Quick folders** let you move a file to a frequently used folder in two taps.

- Click the 📌 icon next to a folder to pin / unpin it.
- Pinned folders appear in the move modal.

---

## Responsive Layout

| Screen width | Mode |
|-------------|------|
| > 700 px | Split view: list on the left, player on the right |
| ≤ 700 px | Full-screen list, player as overlay |
