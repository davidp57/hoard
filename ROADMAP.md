# Roadmap — Hoard

## v1.0 — MVP (done)

- [x] Filesystem browser with breadcrumb navigation
- [x] Integrated HTML5 video player with seek bar and controls
- [x] Auto-save playback position every 5 s
- [x] Resume at last position on re-open
- [x] Visual status in file list: unseen / in-progress (% + bar) / watched (≥ 90 %)
- [x] Move file to predefined folder (quick modal)
- [x] Delete file/folder with confirmation
- [x] Touch gestures: swipe-seek, swipe-volume, double-tap ±10 s, tap = play/pause
- [x] Keyboard shortcuts: Space, ←→ seek, ↑↓ volume
- [x] Responsive: split-view on desktop, full-screen overlay on mobile
- [x] Docker + docker-compose for Synology deployment

## v1.1 — Quality & Sort *(next)*

- [ ] **Sort controls** in file list: by name (asc/desc), date modified, size, watch status
- [ ] **Fullscreen button** on player + `F` shortcut
- [ ] **Playback speed** selector (0.5×, 1×, 1.5×, 2×)
- [ ] Mark file as watched / unwatched manually (right-click / long-press)

## v1.2 — Navigation & Tags

- [ ] **Free-move**: destination picker that browses the filesystem (folder tree)
- [ ] **Rename** file/folder inline
- [ ] **Arbitrary tags** on files (e.g. "excellent", "à finir") — stored in SQLite, shown as badges in the list
- [ ] Filter list by tag

## v1.3 — Media & Subtitles

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
