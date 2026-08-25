# Hoard — Developer Guide

## Overview

Hoard is a minimal web application with no frontend framework, backed by Python/FastAPI. The design principle is simplicity: all backend logic lives in `main.py`, all UI lives in `index.html`.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12, FastAPI, uvicorn |
| Database | SQLite (native `sqlite3` module, no ORM) |
| Frontend | Vanilla HTML/CSS/JS (single file) |
| Video processing | ffmpeg (via subprocess) |
| Video download | yt-dlp (Python library, lazy import) |
| Tests | pytest + httpx |
| Lint / format | ruff |
| CI/CD | GitHub Actions |
| Deployment | Docker, docker-compose |

---

## Project Structure

```
hoard/
├── backend/
│   ├── main.py              # FastAPI application (all logic)
│   └── requirements.txt     # Production dependencies
├── frontend/
│   └── index.html           # Full UI (inline CSS + JS)
├── tests/
│   ├── conftest.py          # Pytest fixtures + env isolation
│   └── test_api.py          # API endpoint tests
├── .github/workflows/
│   ├── ci.yml               # Lint + tests on every push / PR
│   └── docker-build.yml     # Docker image build on main and tags
├── docker-compose.yml       # Production (Synology)
├── docker-compose.dev.yml   # Dev override (hot-reload)
├── Dockerfile               # Non-root image + HEALTHCHECK + ffmpeg
├── pyproject.toml           # pytest + ruff config
├── requirements-dev.txt     # Dev dependencies (tests + lint)
└── docs/                    # Documentation
```

---

## Backend Architecture (`backend/main.py`)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEDIA_ROOT` | `/media` | Media root path inside the container |
| `DB_PATH` | `/data/progress.db` | SQLite database path |
| `SSL_CERTFILE` | *(unset)* | Path to a PEM certificate file. When set (together with `SSL_KEYFILE`), uvicorn serves HTTPS natively. |
| `SSL_KEYFILE` | *(unset)* | Path to the matching PEM private key file. |
| `JOB_TTL_SECONDS` | `3600` | Seconds a terminal download/export job is kept in memory before being purged. |
| `DOWNLOAD_SOCKET_TIMEOUT` | `30` | Seconds of socket silence before yt-dlp aborts a download. Without it, a server that goes quiet hangs the sequential worker indefinitely. |
| `LOG_LEVEL` | `INFO` | Logging level for the `hoard` logger (audit trail). |
| `LOG_DIR` | `<DB_PATH dir>/logs` | Directory for the rotating log file. Empty string disables file logging (stdout only) — the test suite sets it empty. |
| `LOG_RETENTION_DAYS` | `30` | `backupCount` of the `TimedRotatingFileHandler` (daily rotation at midnight). |
| `RESTART_SUPERVISED` | *(auto)* | `0`/`1`. Overrides the container auto-detection (`/.dockerenv`) used to word the restart confirmation in the UI. |
| `HOARD_AUTH_USER` | *(unset)* | Username for optional HTTP Basic auth. Auth is enabled only when both this and `HOARD_AUTH_PASS` are set. |
| `HOARD_AUTH_PASS` | *(unset)* | Password for optional HTTP Basic auth. |

### Path Safety

Every file access goes through `safe_path(rel_path)`, which verifies the resolved path stays under `MEDIA_ROOT`. Any path traversal attempt returns a 400 error.

```python
def safe_path(rel: str) -> Path:
    resolved = (MEDIA_ROOT / rel).resolve()
    if not str(resolved).startswith(str(MEDIA_ROOT.resolve())):
        raise HTTPException(400, "Invalid path")
    return resolved
```

### Security Headers

An HTTP middleware (`add_security_headers`) injects on every response:
`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
`Referrer-Policy: no-referrer`, and a `Content-Security-Policy`. The CSP allows
`'unsafe-inline'` (required by the single-file inline CSS/JS frontend), the
Google Fonts import (`fonts.googleapis.com` / `fonts.gstatic.com`), and
`blob:`/`data:` sources used by the media and PDF.js viewers. Headers are set
with `setdefault`, so an endpoint may override them if needed.

### Optional HTTP Basic Auth

Set both `HOARD_AUTH_USER` and `HOARD_AUTH_PASS` to require HTTP Basic
authentication on every request (`require_basic_auth` middleware). When either
is unset, auth is disabled and behavior is unchanged. Credentials are compared
in constant time. This is meant for exposing Hoard behind a reverse proxy or
direct HTTPS without a full account system — use HTTPS so the Basic credentials
are not sent in clear text.

### API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/files?path=` | List folder contents |
| GET | `/api/progress?path=` | Read watch progress for a file |
| POST | `/api/progress?path=` | Save `{position, duration}` |
| DELETE | `/api/files?path=` | Delete a file or folder |
| POST | `/api/files/move?path=` | Move to `{destination}` (relative path) |
| POST | `/api/files/mkdir` | Create a folder `{path}` |
| POST | `/api/files/rename?path=` | Rename to `{new_name}` (base name only); migrates progress/segments, including folder descendants |
| GET | `/api/subtitles?path=` | List sidecar subtitles for a video (same folder, sharing its stem) |
| GET | `/api/subtitle?path=` | Serve a sidecar subtitle converted to WebVTT (.srt/.ass → VTT, .vtt passthrough) |
| POST | `/api/files/cut` | Cut video via ffmpeg `{path, start, end, output}` |
| GET | `/api/segments?path=` | List segments for a file (ordered by creation) |
| POST | `/api/segments?path=` | Add a segment `{seg_in, seg_out}` → `{id}` |
| DELETE | `/api/segments/{id}` | Delete a segment by id |
| POST | `/api/files/export-segments?path=` | Export segments `{mode, destination, keep_original}` — starts a background job |
| GET | `/api/jobs` | Status of ongoing background jobs (ffmpeg cuts, downloads) |
| GET | `/api/quick-folders` | List pinned folders |
| POST | `/api/quick-folders` | Pin a folder `{path}` |
| DELETE | `/api/quick-folders?path=` | Unpin a folder |
| GET | `/api/initial-sweep?path=` | Read the effective initial-sweep config for a folder |
| POST | `/api/initial-sweep` | Set a folder override `{path, seconds}` |
| DELETE | `/api/initial-sweep?path=` | Remove a folder override and fall back to the global default |
| GET | `/api/browse?path=` | Browse the directory tree (used by the move modal) |
| GET | `/api/settings` | Read user settings |
| POST | `/api/settings` | Save user settings |
| GET | `/api/media-info?path=` | Read on-demand playback metadata via ffprobe |
| GET | `/api/file?path=` | Serve any media file (video/image/audio/PDF) with `Range` support (native seeking) |
| GET | `/api/transcode?path=` | Transcoded stream via ffmpeg |
| GET | `/api/gallery/list?path=` | Ordered sequence of a gallery folder (own level): `{count, items:[{path, type}]}` |
| GET | `/api/thumbnail?path=` | On-the-fly downscaled JPEG thumbnail of an image (ffmpeg, no cache) |
| GET | `/api/archive/list?path=` | Ordered image names inside a ZIP/CBZ/CBR archive |
| GET | `/api/archive/image?path=&index=` | Serve the Nth image from an archive |
| GET | `/api/archive/thumbnail?path=&index=` | Downscaled thumbnail of the Nth archive image (ffmpeg) |
| POST | `/api/download` | Download a web video via yt-dlp `{url, cookies?, referer?, title?}` |
| POST | `/api/jobs/{job_id}/cancel` | Cancel a pending or running download job |
| DELETE | `/api/jobs/{job_id}` | Remove a completed/failed/cancelled job from the in-memory store |
| GET | `/api/downloads` | Persistent download history `?limit=&offset=&status=` → `{total, items}` |
| DELETE | `/api/downloads` | Clear the whole history (files untouched) |
| DELETE | `/api/downloads/{id}` | Remove one history entry |
| POST | `/api/downloads/{id}/retry` | Queue the same URL again from a history entry → `{job_id}` |
| GET | `/api/logs` | Tail of the log file `?lines=&level=` → `{enabled, path, retention_days, lines}` |
| POST | `/api/restart` | Terminate the process so the supervisor restarts it `{force?}` → `{ok, supervised}` |

### Galleries

A folder is treated as a **gallery** — a single media read page by page — when it is a
**leaf** folder: more than 3 images, no video, and **no sub-folders** (own-level scan
only, natural sort). A folder that contains sub-folders is a browsable container, so a
folder of galleries shows each sub-folder as its own gallery instead of flattening
everything into one huge sequence. `/api/files` reports a gallery with
`media_type: "gallery"` plus its own `progress` (resume is anchored on the folder path:
`position` = page index, `duration` = page count). Archives (`.cbz`/`.cbr`/`.zip`) are
the other gallery support and share the same viewer.

Non-image files inside a gallery are **passengers** (PDF/audio/archive/text): they
keep their position in the sequence and are previewed (PDF first page and text are
rendered client-side; others show an icon). Unsupported files are skipped. The
thumbnail strip serves the **full images, downscaled by the browser** (`/api/file` /
`/api/archive/image`), lazily (only when scrolled into view) — this keeps thumbnailing
off the NAS CPU. The ffmpeg thumbnail endpoints (`/api/thumbnail`,
`/api/archive/thumbnail`) remain as a lightweight fallback, hard-capped at
`THUMBNAIL_MAX_CONCURRENCY` concurrent processes (excess requests get 503), but are not
on the gallery hot path.

### Native Playback Versus Transcode

Hoard now fetches `/api/media-info` before playback when possible, then uses the returned container and codec metadata to decide whether native playback is likely safe.

The frontend applies a layered decision ladder:

1. `video.canPlayType()` against the combined container/codecs MIME string.
2. `navigator.mediaCapabilities.decodingInfo()` when the browser exposes it and the metadata is complete enough.
3. `/api/file` by default for the safe baseline and for `probe` formats such as HEVC-in-MP4, even if browser capability APIs stay conservative.
4. `/api/transcode` immediately only for explicit `fallback` formats, or later when native playback still fails at load time.

See `docs/native-playback.en.md` for the compatibility matrix and the implemented strategy.

### SQLite Schema

```sql
CREATE TABLE progress (
    path TEXT PRIMARY KEY,
    position REAL DEFAULT 0,
    duration REAL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quick_folders (
    path TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE initial_sweep_folders (
    path TEXT PRIMARY KEY,
    seconds INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE segments (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    path    TEXT NOT NULL,
    seg_in  REAL NOT NULL,
    seg_out REAL NOT NULL
);
-- index: idx_segments_path ON segments(path)

CREATE TABLE downloads (
    id          TEXT PRIMARY KEY,   -- job uuid
    url         TEXT NOT NULL,
    title       TEXT,               -- bookmarklet page-title hint
    output_name TEXT,               -- final filename
    output_path TEXT,               -- path relative to MEDIA_ROOT
    status      TEXT NOT NULL,      -- pending|resolving|running|done|error|cancelled|interrupted
    error       TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    referer     TEXT                -- needed to replay a direct CDN URL
);
-- index: idx_downloads_created ON downloads(created_at DESC)
```

### Initial Sweep

Initial sweep lets Hoard start a **brand-new video** at a configured offset instead of `0`.

- Global default: stored in the regular `settings` table as `initial_sweep_seconds`
- Folder override: stored in `initial_sweep_folders`, keyed by relative folder path
- Player action: the current playback position can be saved directly as the folder override from a single compact control in the player
- Folder override wins over the global default
- `0` means disabled
- Saved playback progress always wins over any initial-sweep rule

### Background Jobs

Video cuts (`/api/files/cut`) run in individual daemon threads. Web downloads use a sequential queue:

- **Phase 1 (immediate thread)**: when `POST /api/download` is called, a dedicated thread starts immediately, sets the job to `resolving`, fills in a filename preview from the `title` hint, then transitions to `pending` and adds the job to `queue.Queue`.
- **Phase 2 (queue worker)**: a single daemon thread (`dl-worker`) dequeues jobs one at a time and runs the yt-dlp download, preventing bandwidth overload.

**Job status lifecycle:** `pending` → `resolving` → `pending` (with filename) → `running` → `done` / `error` / `cancelled`. History rows can additionally carry `interrupted`, set at startup for jobs the process never finished.

All job state is held in memory in `_jobs: dict[str, dict]`. Fields prefixed with `_` are private and stripped before JSON serialization by `_job_for_api()`. The `/api/jobs` endpoint lets the frontend poll for progress.

**Download persistence.** `_jobs` is the hot store only — entries are purged `JOB_TTL_SECONDS` after reaching a terminal state and vanish on restart. Every meaningful transition of a `download` job is therefore mirrored into the `downloads` table by `_persist_download()`, which the `/api/downloads` history reads back. A DB failure there is logged and swallowed: persistence must never break a download.

At startup, `mark_interrupted_downloads()` flips any row still in a non-terminal state to `interrupted` — the process died mid-download, and without this the history would show jobs stuck `running` forever. Retention is driven by the `download_history_days` setting (`0` = keep forever, the default) and applied by `_purge_download_history()`.

**Retry (BL-084).** `_queue_download()` is shared by `/api/download` and the retry endpoint, so a relaunched download goes through the same SSRF validation, destination and sequential queue — a history row is not a free pass, the URL is revalidated. The `referer` is persisted precisely so a retry of a direct CDN URL survives origin checks; cookies are deliberately not stored (session credentials), so authenticated sites depend on the `download_cookies_path` setting.

**Worker resilience (BL-078).** `_download_worker_loop` catches every exception escaping `_run_download`. Before that fix, any unexpected error (a broken yt-dlp import, a job removed mid-flight) propagated out of the `while True` loop and killed the `dl-worker` thread permanently: all later downloads then sat in `pending` forever with no error surfaced anywhere. The handler now logs the traceback, marks the job `error`, and keeps the thread alive.

**Silent skip (BL-079).** yt-dlp does **not** overwrite an existing target and does **not** raise when it skips: `extract_info(download=True)` returns normally and the progress hook still fires `finished`. Hoard used to read that as success, so a download whose filename was already taken was reported `done` with no file written — the bookmarklet sends `document.title`, and one site often gives many videos the same title, so this lost files in bulk. Three guards now apply:

1. `_unique_output_stem()` frees the name up front (`Video.mp4` → `Video (2).mp4`), testing the `stem + "."` prefix via `iterdir()` — not `glob()`, since a stem may contain `[`.
2. The progress hook counts `downloading` events. Zero events means no bytes moved, i.e. a skip; the job becomes an `error` explaining the collision. This is the net for downloads started without a title, where the name cannot be reserved in advance.
3. `_confirm_download_landed()` refuses to mark a job `done` unless the file is actually on disk, and logs the absolute path and size.

The stored filename comes from `info["requested_downloads"][0]["filepath"]` — what yt-dlp actually wrote. The old code rebuilt it from `prepare_filename()` and forced `merge_output_format` onto the suffix, so a single-stream download written as `.webm` was recorded as a `.mp4` that never existed.

Titles are escaped with `_outtmpl_literal()` before entering the output template: `%` starts a field reference, so `Best of 50%(off) deal` produced the file `Best of 50NAeal.mp4`.

### Download Endpoint (`POST /api/download`)

**Request body** (`DownloadRequest`):

```json
{ "url": "https://cdn.example.com/video.mp4", "cookies": "name=value; other=foo", "referer": "https://example.com/posts/123" }
```

- `url` — required. The web page or direct video URL.
- `cookies` — optional. Raw `document.cookie` string captured by the bookmarklet. Converted to Netscape format and passed to yt-dlp.
- `referer` — optional. The original page URL. When provided, it is sent as the `Referer` HTTP header so CDNs that check the origin accept the request. The bookmarklet sets this automatically when a direct `<video>` source is detected.

**Response:**

```json
{ "job_id": "abc123" }
```

**Security (SSRF protection):** The endpoint rejects `file://` URLs and any host that resolves to localhost or RFC-1918 private addresses (`127.*`, `::1`, `192.168.*`, `10.*`, `172.*`).

**Cookie resolution order:**
1. Persistent `cookies.txt` file (path from `download_cookies_path` setting), if it exists.
2. Inline cookies from the request body, written to a temporary file.

The `download_cookies_path` setting is validated when saved via `POST /api/settings` (`_validate_cookies_path()`): the path must be absolute, end with `.txt`, exist as a readable file, otherwise the save is rejected with HTTP 422. An empty string clears the setting. This prevents pointing yt-dlp at an arbitrary file.

**yt-dlp options used:** `bestvideo+bestaudio/best`, `merge_output_format: mp4`. Output is saved to the `download_folder` setting (relative to `MEDIA_ROOT`, created if needed).

---

## Frontend Architecture (`frontend/index.html`)

The frontend is a single HTML file with inline CSS and JS. No framework, no bundler.

### JS Organisation

The JS is organised into commented functional sections:

- **Config & state** — constants, global variables
- **API helpers** — reusable `fetch` wrappers
- **Navigation** — folder loading, breadcrumb, LRU cache
- **File list rendering** — file list DOM rendering
- **Player** — controls, seekbar, position saving
- **Touch gestures** — touch event handling
- **Keyboard shortcuts** — `keydown` handler
- **Modals** — move, browse, cut
- **Quick folders** — pin management

### CSS Variables

All colour tokens are defined in `:root`:

```css
:root {
  --bg: #0e0e0f;
  --surface: #161618;
  --accent: #e8ff47;
  --seen: #3a5a3a;
  --inprogress: #5a4a1a;
  /* ... */
}
```

### Responsive

- Breakpoint at **700 px**: above, split view (list + player). Below, full-screen list with player as overlay.
- `dvh` used throughout to avoid mobile viewport unit issues.

### PWA Shell

- `frontend/manifest.webmanifest` provides install metadata for supported browsers and home-screen launchers.
- `frontend/service-worker.js` caches only the app shell (`/`, favicon, manifest) and explicitly avoids `/api/*` requests, so installability does not imply offline NAS browsing or playback.
- The frontend registers the service worker only in secure contexts and applies safe-area padding so the standalone shell behaves better on tablets and iOS home-screen launch.

---

## Local Development

### Quick setup

```bash
git clone https://github.com/davidp57/hoard.git
cd hoard
python -m venv .venv
.venv\Scripts\activate          # or: source .venv/bin/activate
pip install -r requirements-dev.txt

$env:MEDIA_ROOT = "$(pwd)\dev-media"
$env:DB_PATH    = "$env:TEMP\hoard-dev.db"
uvicorn backend.main:app --reload --port 8000
```

### Development script

```powershell
# dev.ps1 — starts the server with the right variables
.\dev.ps1
```

---

## Tests

```bash
python -m pytest tests/ -v
```

Tests use `httpx.AsyncClient` with FastAPI's `TestClient`. Each test runs in an isolated temporary directory (`tmp_path`). Ruff and pytest configuration is in `pyproject.toml`.

Coverage report is written to `coverage.xml`.

---

## Lint and Format

```bash
ruff check .          # lint
ruff format --check . # format check
ruff format .         # auto-format
```

---

## CI/CD

### ci.yml

Triggered on every push and PR:
1. `ruff check .`
2. `ruff format --check .`
3. `python -m pytest tests/ -v --cov`

### docker-build.yml

Triggered on push to `main` and `v*.*.*` tags:
- Multi-platform build (`linux/amd64`, `linux/arm64`)
- Push to `ghcr.io/davidp57/hoard`
- Tag `main` for the main branch, semver tags for releases

---

## Conventions

- **No ORM**: all SQLite queries are hand-written with bound parameters (`?`).
- **No breaking API changes** without updating this file and `docs/installation.*.md`.
- **Pydantic typing** only for POST request bodies.
- **Paths** are always stored and transmitted **relative to `MEDIA_ROOT`**.
- CSS variables for all colour tokens — no hardcoded colours in HTML.
- One single `index.html`: do not split the frontend into multiple files.

---

## Adding an Endpoint

1. Add the function in `backend/main.py` with its `@app.<method>` decorator.
2. Add the test case in `tests/test_api.py`.
3. Update the endpoint table in this file and in `CLAUDE.md`.
4. Implement the client-side call in `frontend/index.html`.
