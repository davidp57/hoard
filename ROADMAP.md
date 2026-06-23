# Roadmap — Hoard

## v1.0 — Initial release *(done)*

- [x] Filesystem browser with breadcrumb navigation
- [x] Integrated HTML5 video player with seek bar and controls
- [x] Auto-save playback position every 5 s; resume at last position on re-open
- [x] Visual status in file list: unseen / in-progress (% + bar) / watched (≥ 90 %)
- [x] Move file to predefined folder (quick modal) + delete with confirmation
- [x] Touch gestures: swipe-seek (3 vertical speed zones), swipe-volume, multi-tap seek, tap = play/pause
- [x] Keyboard shortcuts: Space, ←→ seek, ↑↓ volume
- [x] Responsive: split-view on desktop, faux-fullscreen overlay on mobile/iOS
- [x] On-the-fly H.265 → H.264 transcoding with auto-fallback
- [x] Settings page: home folder, sort order, watched threshold, privacy timeout
- [x] PIN lock (numeric, SHA-256 hashed) with configurable timeout
- [x] Fully configurable touch gestures (enable/disable per category, sensitivity, zones)
- [x] Fit/Fill toggle button in player toolbar
- [x] Page Visibility API privacy: auto-close player after configurable inactivity timeout
- [x] Full bilingual documentation (EN + FR): user guide, installation, developer and getting-started guides
- [x] Docker + docker-compose for Synology deployment (ghcr.io image)

## v2.0 — Web Download *(done)*

- [x] Video download via yt-dlp: bookmarklet + 📥 button in the header
- [x] Background bookmarklet: submits download via `fetch()`, shows live status dialog on the current page (no navigation)
- [x] Smart video source detection: captures `<video>.currentSrc`, iframe detection (BunnyCDN / YouTube / Vimeo), 6 capture strategies
- [x] Server-side HTML sniffing fallback: scans `<video>`, `<source>`, `<iframe>`, `<meta og:video>`, inline `<script>`, `data-*` — retries yt-dlp automatically if a source is found
- [x] Download queue widget: 📥 badge, live modal with progress bars, dismiss completed jobs
- [x] Sequential queue: one download at a time via `queue.Queue`, stop/cancel button, automatic `.part` file cleanup on cancel
- [x] Auto-refresh file browser when a download completes
- [x] Cookie passthrough (bookmarklet + persistent `cookies.txt`), Referer passthrough
- [x] HTTPS support: native via `SSL_CERTFILE` / `SSL_KEYFILE` env vars (no reverse proxy needed)
- [x] SSRF protection on `/api/download` (rejects `file://`, localhost, RFC-1918)

## v1.2 — Player & Sort *(done)*

- [x] **Unified multi-level seek** (BL-021): 4 configurable seek durations (short/medium/long/x-long) shared by keyboard shortcuts, touch double-tap zones, and player buttons; extended keyboard shortcut set (M, A, I, O, C, D, Delete, S, PageDown/PageUp, ?); move/cut/delete modals usable in native fullscreen via `<dialog>.showModal()`
- [ ] **Sort controls** in file list: by name (asc/desc), date modified, size, watch status (BL-002)
- [x] **Fullscreen button** on player + `F` shortcut (BL-021)
- [x] **Playback speed** selector (0.5×, 1×, 1.5×, 2×) (BL-010)
- [ ] Mark file as watched / unwatched manually (right-click / long-press) (BL-003)

## v1.3 — Navigation & Tags *(done)*

- [x] **Multiple home roots**: configure named root folders so the home screen lists several roots (BL-023)
- [x] **Free-move**: destination picker that browses the filesystem (folder tree) (BL-005)
- [x] **Arbitrary tags** on files (e.g. "excellent", "à finir") — stored in SQLite, shown as badges in the list (BL-007)
- [x] **Filter list by tag** — tag filter bar appears dynamically in the sort bar (BL-007)
- [x] **Search across filenames** — recursive search field in the sort bar, scoped to the current folder (BL-012)
- [ ] **Rename** file/folder inline (BL-006)

## v1.4 — Media & Subtitles

- [ ] **Subtitle support**: auto-detect `.srt` / `.ass` files in the same folder and offer them as text tracks (BL-008)
- [x] **Auto-refresh** file list every 30 s when the tab is active and video is paused (BL-009)
- [x] Display video metadata under the player title (duration, resolution, codec, bitrate) via `ffprobe` (BL-016)

## v2.1 — Multi-Segments & Gamepad Polish *(done)*

- [x] **Multi-segment export** (BL-047–051): replace single IN/OUT cut with multi-segment system; segments stored in SQLite; export individual or merged via FFmpeg lossless concat; full keyboard and gamepad support (`I`/`O`/`E`, `L1+Y`/`R1+Y`/`L1+R1+Y`)
- [x] **Auto-play next in fullscreen**: after delete/move/cut of the current file in fullscreen, the next file starts automatically and fullscreen is restored
- [x] **Volume OSD**: on-screen volume bar with icon, level, and percentage; auto-hides after 2.5 s
- [x] **Fullscreen progress indicator**: zoomed progress bar overlay in native fullscreen (time remaining, global bar, zoomed segment)
- [x] **Gamepad fullscreen dialogs** (BL-046): delete and move dialogs visible and navigable in native fullscreen on SteamDeck/Edge
- [x] **Gamepad cursor preservation** (BL-043/052): cursor no longer resets after file actions or auto-play next
- [x] **Default home root** (BL-040): designate a root as the startup destination; navigate there directly without the root-picker screen

## v2.3 — Security, Quality & UX *(done)*

- [x] **Optional HTTP Basic auth** (BL-011): enable via `HOARD_AUTH_USER` / `HOARD_AUTH_PASS`, disabled by default
- [x] **Hardened PIN hashing** (BL-030): scrypt with per-PIN salt; transparent migration from legacy SHA-256
- [x] **HTTP security headers** (BL-029): `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, CSP
- [x] **Audit logging** (BL-036): INFO trail for delete/move/download/settings + client IP, WARNING on failed PIN
- [x] **Robustness**: `MEDIA_ROOT` thread-safety (BL-032), DB-first delete/move atomicity (BL-034), job-store TTL purge (BL-033), progress-map covering index (BL-035), cookies-path validation (BL-031)
- [x] **Frontend**: fetch timeout + network feedback (BL-037), accessibility pass (BL-039), touch gesture discovery overlay (BL-038), keyboard-help contrast fix (BL-065)

## v2.3 — Player desktop UX polish *(done)*

- [x] **Windowed fullscreen by default on desktop** (BL-066): `F` = in-window immersive fullscreen, `Shift+F` = real OS fullscreen; touch devices keep the real API
- [x] **Escape goes up one level** (BL-068): keyboard navigation mirrors the gamepad (Esc = B / `nav_back`), shared `navigateUp()`
- [x] **Remove dead `/api/stream` endpoint** (BL-067): playback fully consolidated on `/api/file`

## v2.0 — Platform

- [x] **Basic authentication** delivered as optional HTTP Basic auth (BL-011) — see v2.3
- [ ] **Light theme** toggle (persisted in localStorage)
- [ ] **PWA** manifest + service-worker: installable on iPad / Windows laptop
- [ ] **Search** across all filenames in MEDIA_ROOT
- [ ] **Multi-user** watch progress (per-user SQLite rows)

## v1.5 — Gamepad / Controller Support *(done)*

- [x] **Gamepad support** (BL-024): Gamepad API, 4-layer button system (base / L1 / R1 / L1+R1), full player controls (play/pause, seek multi-level, volume, fullscreen, watched toggle, aspect ratio, quick-folder moves), file browser cursor navigation, analog left-stick scrubbing, analog right-stick volume, layer HUD badge, dynamic button-map overlay (Start), connection/disconnection toasts, haptic feedback (Chrome), configurable deadzone and on/off toggle in Settings

## v1.7 — Alternative Media Readers *(planned)*

- [ ] **Image viewer** (BL-053+054): browse folders of images with keyboard/gamepad, two display modes (page-width / full-page)
- [ ] **Archive reader** (BL-055): open `.zip`, `.cbz`, `.cbr` comic archives directly in the image viewer
- [ ] **PDF reader** (BL-056): PDF.js-powered reader with page navigation, zoom, keyboard/gamepad control, and saved progress
- [ ] **Audio player** (BL-057): native audio playback for `.mp3`, `.flac`, `.ogg`, `.m4a`, `.aac`, `.wav`, `.opus` using existing player infrastructure

---

> Items within each milestone are roughly ordered by priority.
> The roadmap is intentionally kept small — complexity is the enemy here.
