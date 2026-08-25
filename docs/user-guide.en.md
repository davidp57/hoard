# Hoard — User Guide

## Overview

Hoard is a web-based media file browser. It lets you navigate a network drive (NAS), play videos, view images and comic archives, listen to audio files and read PDFs directly in the browser, and remember where you left off.

---

## Main Interface

The interface is split into two areas:

- **Left (or full-screen on mobile):** the file browser
- **Right (or full-screen overlay on mobile):** the video player

### File Browser

The browser displays the contents of a folder. A **breadcrumb** at the top lets you navigate up. The **🏠** button returns to the home screen.

### Home Screen and Home Roots

If no home roots are configured, the browser opens directly at `MEDIA_ROOT`. If home roots are defined (via **Settings → Home roots**), pressing **🏠** shows a selection screen listing each named home root. Click one to navigate directly to it.

Each file or folder is shown with:

- Its name
- A **watch status indicator** (for video files):
  - Neutral background → **unseen**
  - Yellow background + progress bar + percentage → **in progress**
  - Green background → **watched** (≥ 90 % viewed)

### Search

A **🔍** field is available in the sort bar. The search is case-insensitive and recursive within the current folder. Results replace the list; clearing the field (or pressing ✕) returns to normal browsing.

### Tags and Tag Filtering

Any file or folder can carry **free-form text tags** (e.g. `excellent`, `to-finish`). Tags are stored in SQLite and displayed as coloured badges in the list.

| Action | How |
|--------|-----|
| Add / remove a tag | Click the **🏷** button next to the entry |
| Filter the list by a tag | Click a badge in the **tag filter bar** below the sort bar |
| Clear the filter | Click the same badge again, or navigate to another folder |

The tag filter bar appears automatically as soon as a folder contains at least one tagged file.
|--------|-------------|
| **▶ Play** | Opens the video in the player |
| **🏷 Tags** | Opens the tag management modal |
| **📁 Move** | Opens the move modal (pinned folders + free-pick browser) |
| **✏ Rename** | Opens the rename dialog (`R` key) |
| **🗑 Delete** | Deletes the file after confirmation |

### Moving to Any Folder

The move modal offers two modes:

- **Pinned folders**: one-tap move to a predefined folder.
- **📂 Browse…**: opens a destination picker that browses the full folder tree so you can choose any destination.

---

## Alternative Media Viewers

In addition to videos, Hoard can open several other file types directly in the interface.

### Images

JPG, PNG, GIF, WEBP, BMP, TIFF, and AVIF files open in an integrated image viewer.

- **← / →** (keyboard or buttons): previous / next image in the folder
- **▣ button**: toggle between fit-width and full-page display
- **✕**: close the viewer

### Galleries (image folders)

A folder containing several images (more than 3) and no video is treated as a
**gallery**: it shows up in the list as a single media (🖼️ icon, progress bar, watched
state), and opening it shows the first image right away instead of the file list.

- You read images one after another; the position is saved and resumed on reopen, just
  like a video.
- A gallery is a single image folder. A folder that **contains sub-folders** stays browsable and shows each sub-folder as its own gallery (so a folder of albums opens as a list of galleries, not one giant sequence).
- A **thumbnail strip** under the image acts as a seek bar: click a thumbnail to jump.
- **Zoom**: mouse wheel (zoom centered on the cursor), click-drag to pan, double-click to
  toggle zoom ↔ fit. Keyboard: `+` / `-` to zoom, `0` to reset; arrows pan while zoomed
  (otherwise they go to the previous / next image). Gamepad: left stick pans, right stick
  ↕ zooms.
- With a mouse (desktop), hover a thumbnail to reveal ✕ (delete that image) and › (move
  that image). With keyboard/gamepad, delete/move act on the **whole gallery** (like a
  movie), and `W` marks it watched / unwatched.
- A stray non-image file (PDF, text…) stays accessible as a **passenger**: it keeps its
  place in the sequence with a preview.

### Comic/manga archives (.cbz, .zip, .cbr)

Image archives are galleries too: they open page by page in the same viewer, with the
thumbnail strip.

- Navigation identical to the image viewer (← / →)
- Current page is saved so you can resume where you left off
- `.cbr` requires `unrar-free` to be installed on the server

### PDF

PDF files are rendered directly in the browser via PDF.js.

- **← / →**: previous / next page
- **− / +**: zoom out / zoom in
- **▣ button**: toggle between fit-width and original size
- Current page is saved

### Audio (.mp3, .flac, .ogg, .m4a, .aac, .wav, .opus)

Audio files open in a minimal player.

- Clickable progress bar
- ◀◀ / ▶ / ▶▶ buttons (seek ±10 s, play/pause)
- Position is saved

### Watch Progress

The **watched / in-progress / unwatched** status works for all media types, not just videos. The percentage is computed the same way (position / duration for video and audio; page / total for PDF and archives).

---

## Video Player

### Controls

| Element | Role |
|---------|------|
| **Progress bar** | Shows and controls position in the video |
| **⏮ / ⏭** | Seek back / forward — medium (30 s default, configurable) |
| **◀◀ / ▶▶** | Seek back / forward — short (10 s default, configurable) |
| **▶ / ⏸** | Play / Pause |
| **🔊** | Mute/unmute |
| **Volume** | Volume slider |
| **🐢 / 🐇** | Speed cycle: 0.5× → 1× → 1.5× → 2× (reset on each file open) |
| **⛶** | Fullscreen |

When you enter fullscreen, Hoard hides the controls automatically to maximize the video area.

- On desktop, move the mouse or use keyboard shortcuts to bring the controls back temporarily.
- On touch devices, only the existing bottom-centre tap zone near the controls should show or hide them.

### Video Metadata

When a file is playing, the codec, resolution, duration, and bitrate are shown below the filename (fetched from the server via `ffprobe`).

### Auto-resume

Position is saved automatically every 5 seconds. When you re-open a file, playback resumes from where you stopped.

### Smarter Native Playback Detection

Before falling back to server-side transcoding, Hoard now checks whether the current browser is likely able to play the original file natively.

- MP4/H.264/AAC remains the safest native baseline.
- For more variable formats such as HEVC, AV1, or WebM, Hoard probes browser support first when metadata is available.
- If native playback is not confirmed, Hoard switches to the transcoded stream automatically.

### Initial Sweep For New Videos

You can configure an **initial sweep** offset for videos that have **no saved progress yet**.

- A **global default** is available in **Settings → Player**.
- While playing a video, a single **folder start** action can save the **current playback position** as the default start for that folder.
- `0` means disabled.
- A folder override takes precedence over the global default.

This rule only applies to brand-new videos. Once a file has saved progress, Hoard always resumes from the real saved position instead.

### IN/OUT Markers (trim)

The `[IN` and `OUT]` buttons define a restricted playback zone (without modifying the file). The ✂ button triggers a physical file cut via ffmpeg.

### Auto-refresh File List

The file list refreshes automatically every 30 seconds when the tab is visible, the video is paused, and no search is active. This makes new files appear without a manual page reload.

---

## Touch Gestures

Gestures work directly on the video image.

> The first time you open a video on a touch device, a short help screen introduces the main gestures. Tap **Compris** (Got it) to dismiss it; it will not appear again.

### Single Tap

| Area | Action |
|------|--------|
| Narrow centre band (upper area) | Play / Pause |
| Narrow bottom-centre strip | Show / hide controls in fullscreen |

### Double Tap

| Area | Action |
|------|--------|
| Left edge (< 20 % width) | Seek back 30 s |
| Right edge — bottom third | Seek forward — medium (30 s default) |
| Right edge — middle third | Seek forward — long (60 s default) |
| Right edge — top third | Seek forward — extra-long (120 s default) |
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
| `↑ / ↓` *(no media)* | Move cursor in the file list |
| `↑ / ↓` *(media playing)* | Volume +/− 10 % |
| `Enter` | Open the item under the cursor |
| `Space` | Play / Pause |
| `← / →` | Short seek (10 s default) |
| `Shift + ← / →` | Medium seek (30 s default) |
| `Ctrl + ← / →` | Long seek (60 s default) |
| `Alt + ← / →` | Extra-long seek (120 s default) |
| `F` | Fullscreen (in-window on desktop) |
| `Shift + F` | Real OS fullscreen (on desktop; otherwise use `F11`) |
| `Esc` | Exit fullscreen → close the player → go up one level in the tree |
| `M` | Mute / Unmute |
| `C` | Subtitles (cycle tracks / off) |
| `[ / ]` | Speed − / + (0.5× → 1× → 1.5× → 2×) |
| `A` | Cycle aspect ratio (Fit / Fill / …) |
| `W` | Toggle watched / unwatched |
| `PageDown / PageUp` | Next / previous video in folder |
| `I / O` | Set IN / OUT marker |
| `E` | Open Trim window |
| `D` | Open Move window |
| `R` | Rename (current file or selected entry) |
| `Delete` | Delete current file |
| `S` | Save folder start position |
| `?` | Show / hide keyboard help |

---

## Gamepad / Controller Support

Hoard supports game controllers via the browser's **Gamepad API** (Xbox, PlayStation DualSense, Switch Pro, Steam Deck, iPhone with a Bluetooth controller, etc.).

### Connecting

- Plug in or pair the controller, then press any button while Hoard is open.
- A « 🎮 Controller connected » toast confirms detection.
- **Steam Deck / Firefox**: Firefox only fires `gamepadconnected` after a button press. A toast « Press a button to activate the controller » appears if the device is detected but not yet active.

### Actions — Video Player

| Button | Base | + L1 | + R1 | + L1+R1 |
|--------|------|------|------|---------|
| **A** | Play / Pause | Subtitles | Move → Folder 1 | Jump to 0% |
| **B** | Close player | — | Move → Folder 2 | — |
| **X** | Toggle watched | Aspect ratio | Move → Folder 3 | Jump to 50% |
| **Y** | Fullscreen | Jump to 0% | — | Jump to 100% |
| **D-pad ←/→** | Seek medium | Seek long | Seek extra-long | — |
| **D-pad ↑/↓** | Volume ±10% | Prev/next file | Jump to 25%/75% | — |
| **Select** | Open Settings | — | — | — |
| **Start** | Show button map | — | — | — |
| **L3** (stick click) | Mute / Unmute | — | — | — |
| **R3** (stick click) | Cycle speed (0.5× → 1× → 1.5× → 2× → …) | — | — | — |
| **Left stick X** | Analog scrubbing | — | — | — |
| **Right stick Y** | Analog volume | — | — | — |

### Actions — File Browser (no video open)

| Button | Action |
|--------|--------|
| **D-pad ↑/↓** | Move cursor in the list |
| **Left stick Y** | Move cursor (analog) |
| **A** | Open the selected file or folder |
| **B** | Go up one level |
| **Start** | Open Settings |

### Modifier Layers (L1 / R1)

Hold **L1** or **R1** to access extra command layers. Holding both (L1+R1) activates a fourth layer. A small **corner badge** (e.g. « 🎮 L1 ») shows the active layer.

### Button Map Overlay

Press **Start** (or the « Show button map » button in Settings) to display an overlay listing all actions per layer, dynamically updated with your configured seek durations.

### Controller Settings

In **Settings → 🎮 Controller**:

| Setting | Description |
|---------|-------------|
| **Controller enabled** | Enable / disable gamepad detection entirely |
| **Haptic feedback** | Short vibration on play/pause, seek, watched toggle (Chrome only) |
| **Dead zone** | Stick detection threshold (default 20%). Increase if sticks drift. |

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

**From any web page** — click the bookmarklet. It submits the download **in the background** and injects a live status dialog directly into the current page — no navigation, no opened tab. The dialog progresses through ⌛ "Analyse de l'URL…" → 📥 "Téléchargement… X%" → ✅ "Terminé !" (auto-closes after 4 s). If the queue is busy it shows ⏳ "En attente dans la file… — titre.mp4" until the slot is free. You can cancel the job from the dialog or from the Hoard download queue modal.

> **Sites with a restrictive CSP**: some sites (often ad-heavy streaming sites) block outgoing requests to a third-party domain like Hoard's via their `Content-Security-Policy`. In that case the bookmarklet shows ℹ️ "Site incompatible (CSP)" and automatically opens Hoard in a new tab to finish the download there.

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
- Click **⏹** on a pending or running download to cancel it immediately. Any partial `.part` file left by yt-dlp is deleted automatically.
- **Sequential queue**: downloads run one at a time. New jobs wait in a "pending" state until the current download finishes, preventing bandwidth overload.
- **Downloads continue even if you close the tab**: they run as backend threads on the NAS. When you return to Hoard, the queue widget automatically reconnects to in-progress jobs.
- **Auto-refresh**: when a download completes, the file browser automatically refreshes if you are currently browsing the download folder.

### Download History

The **📥** modal has two parts:

- **In progress** — the current queue (progress, cancel, dismiss), which disappears once emptied.
- **History** — the **permanent** list of everything that was downloaded, stored in the database. Unlike the queue, it survives a NAS restart and never expires.

Each row shows the filename, the date, and the outcome:

| Status | Meaning |
|--------|---------|
| ✓ Done | The file made it. **Aller au fichier** opens its folder and highlights it. |
| ✗ Failed | The download failed. The error message is shown under the row. |
| ⊘ Cancelled | You stopped the download. |
| ⚠ Interrupted (restart) | Hoard stopped mid-download. The file did not make it — start it again. |

**Vider** clears the history (downloaded files are never touched); **✕** removes a single row.

History is kept **without any limit** by default — that is precisely what lets you find an old download again. To bound it: **Settings → Maintenance → Historique des téléchargements**, in days (`0` = unlimited).

### Where Files Land

The 📥 modal shows the destination twice: the relative name (e.g. `Downloads`) and the **full path** (e.g. `/media/Downloads`). When the folder does not exist yet, a "sera créé" note says so.

This matters because the destination folder is **created on demand**: a mistyped setting raises no error, it just creates a folder somewhere else where every download quietly piles up.

### Two Videos, Two Files

When the bookmarklet sends the page title as the filename, two different videos on the same site often carry the **same** title. Hoard now suffixes the name — `Ma video.mp4`, then `Ma video (2).mp4` — exactly like a browser does.

Without that, the downloader saw a file of the same name, **skipped the download silently**, and the video was lost while the UI displayed "Terminé". Should the case still arise (a download started with no filename), the entry now ends as a **failure** with a message explaining what to do, never as "done".

### Settings

| Setting | Description |
|---------|-------------|
| **Seek durations** | Four configurable levels in **Settings → Player**: short (default 10 s), medium (30 s), long (60 s), extra-long (120 s). Used by skip buttons, keyboard shortcuts, and double-taps. |
| **Enable transcoding** | When disabled, Hoard always serves the original file (`/api/file`) without calling the transcoder. Useful if your NAS is slow or your browser can play the format natively. |
| **Default initial sweep** | Start brand-new videos at N seconds instead of 0. Applies only when the file has no saved progress yet. `0` disables it globally. |
| **Home roots** | Named root folders shown on the home screen. Add or remove them in **Settings → Home roots**. |
| **Download folder** | Target folder, relative to the media root (default: `Downloads`). The **full path** is shown under the field, with a warning when the folder does not exist yet — it gets created on the first download. **📂 Parcourir…** picks it by browsing instead of typing. |
| **Cookies file path** | Absolute path to a Netscape `cookies.txt` file. Useful for sites that require authentication. |
| **Download history** | Days of download history kept (**Settings → Maintenance**). `0` = unlimited (default). |

### About Cookies

The bookmarklet forwards `document.cookie` from the source page. Note that **HttpOnly cookies are not accessible to JavaScript** — for sites where those are required (e.g. streaming platforms), export a `cookies.txt` file with a browser extension and specify its path in Settings.

---

## Maintenance

The **Settings → Maintenance** section covers everyday operational tasks.

### Log

Hoard records its events (downloads started, completed, failed, restart requests) in a file kept for **30 days**, on top of the container logs. The log can be read right here:

- Pick how many lines to show (100 / 500 / 2000).
- Filter by level: all, info, warnings, errors.
- **↻** refreshes, **Copier** puts the content on the clipboard (handy for pasting into an issue).

Lines are in chronological order, newest at the bottom.

### Restart Hoard

The **↻ Redémarrer Hoard** button restarts the application without going through Portainer or the NAS. Useful after a low-level setting change, or when something misbehaves.

- If a download is running, Hoard asks for an extra confirmation: restarting **permanently interrupts** it (it will show up as *Interrupted* in the history).
- Once triggered, the page waits for the server to come back and reloads on its own (up to 60 s). Past that, a message suggests checking the container.
- Hoard never restarts itself: the container does (`restart: unless-stopped` in `docker-compose.yml`). Outside a container the button **shuts the application down** — the confirmation message says so explicitly.

---

## Responsive Layout

| Screen width | Mode |
|-------------|------|
| > 700 px | Split view: list on the left, player on the right |
| ≤ 700 px | Full-screen list, player as overlay |

## Install As An App

On browsers that support web app install prompts, Hoard can now be installed as a standalone app instead of staying in a regular tab. On iPad and iPhone, use the browser's **Add to Home Screen** action to get the same standalone launch behavior.

The install shell only caches the app shell assets needed to reopen the interface faster. Hoard still expects a live connection to your NAS for API calls, browsing, and video playback.
