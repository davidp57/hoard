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

## v1.2 — Quality & Sort *(next)*

- [ ] **Sort controls** in file list: by name (asc/desc), date modified, size, watch status
- [ ] **Fullscreen button** on player + `F` shortcut
- [ ] **Playback speed** selector (0.5×, 1×, 1.5×, 2×)
- [ ] Mark file as watched / unwatched manually (right-click / long-press)

## v1.3 — Navigation & Tags

- [ ] **Free-move**: destination picker that browses the filesystem (folder tree)
- [ ] **Rename** file/folder inline
- [ ] **Arbitrary tags** on files (e.g. "excellent", "à finir") — stored in SQLite, shown as badges in the list
- [ ] Filter list by tag

## v1.4 — Media & Subtitles

- [ ] **Subtitle support**: auto-detect `.srt` / `.ass` files in the same folder and offer them as text tracks
- [ ] **Auto-refresh** file list (poll or SSE) to detect new downloads without reloading
- [ ] Display video metadata on hover / detail pane (duration, resolution, codec) via `ffprobe`

## v2.0 — Platform

- [ ] **Basic authentication** (username + password, bcrypt) for LAN-external exposure
- [ ] **Light theme** toggle (persisted in localStorage)
- [ ] **PWA** manifest + service-worker: installable on iPad / Windows laptop
- [ ] **Search** across all filenames in MEDIA_ROOT
- [ ] **Multi-user** watch progress (per-user SQLite rows)

---

> Items within each milestone are roughly ordered by priority.
> The roadmap is intentionally kept small — complexity is the enemy here.
