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

## Video Download

Hoard can download videos from the web using **yt-dlp** and save them directly to your NAS.

### Installing the Bookmarklet

1. Open **Settings** (⚙️ button in the header).
2. Scroll to the **Downloads** section.
3. **Drag** the "📥 Télécharger avec Hoard" link to your bookmarks bar.

### Downloading a Video

**From any web page** — click the bookmarklet. Hoard opens in a new tab with the URL, your browser cookies, and the page title pre-filled in the download queue modal. Click **📥 Télécharger** to start.

> **Smart video source detection**: if a `<video>` element is playing on the page, the bookmarklet captures its direct source URL instead of the page URL. This enables downloading from sites where yt-dlp has no dedicated extractor (Patreon, custom video players, BunnyCDN embeds, etc.). The modal shows a 🎬 hint when a direct source was detected. The original page URL is automatically sent as the `Referer` header so CDNs that verify the origin accept the request.

**From inside Hoard** — click the **📥** button in the header, paste a URL, and confirm.

**Filename hint**: the "Nom du fichier" field is pre-filled with the page title when using the bookmarklet. You can edit it freely before starting the download. If left empty, yt-dlp extracts the title automatically.

### Download Queue

All downloads are tracked in a central queue accessible from the **📥** button in the header:

- A **badge** on the button shows the number of active downloads.
  - Yellow badge = downloads in progress.
  - Green badge = all done (queue has items to dismiss).
- Click the button to open the **download queue modal**, which shows each download with its filename, progress bar, and status.
- Click **✕** next to a completed or failed download to dismiss it from the queue.
- **Downloads continue even if you close the tab**: they run as backend threads on the NAS. When you return to Hoard, the queue widget automatically reconnects to in-progress jobs.

### Settings

| Setting | Description |
|---------|-------------|
| **Download folder** | Target folder, relative to `MEDIA_ROOT` (default: `Downloads`). Created automatically if it does not exist. |
| **Cookies file path** | Absolute path to a Netscape `cookies.txt` file. Useful for sites that require authentication. |

### About Cookies

The bookmarklet forwards `document.cookie` from the source page. Note that **HttpOnly cookies are not accessible to JavaScript** — for sites where those are required (e.g. streaming platforms), export a `cookies.txt` file with a browser extension and specify its path in Settings.

---

## Responsive Layout

| Screen width | Mode |
|-------------|------|
| > 700 px | Split view: list on the left, player on the right |
| ≤ 700 px | Full-screen list, player as overlay |
