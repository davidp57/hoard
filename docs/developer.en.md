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
| `HOARD_SECRET_KEY` | *(generated)* | HMAC key signing the session cookie. Falls back to a `session_secret` row minted on first use. Rotating it revokes every session. |
| `HOARD_COOKIE_SECURE` | `1` | Whether the session cookie carries `Secure`. A setting rather than introspection: behind the Synology reverse proxy the backend only ever sees plain HTTP. |

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

### Optional Authentication

Set both `HOARD_AUTH_USER` and `HOARD_AUTH_PASS` to require authentication on
every request (`require_basic_auth` middleware). When either is unset, auth is
disabled and behavior is unchanged. Credentials are compared in constant time.
This is meant for exposing Hoard behind a reverse proxy or direct HTTPS without a
full account system — use HTTPS so the Basic credentials are not sent in clear text.

Since BL-123 the middleware accepts **either** a signed session cookie **or**
Basic. See *Authentication (BL-011, BL-123)* below for the cookie, the withheld
`WWW-Authenticate` header and the exempt shell paths.

**One route is exempt: `/healthz`.** The container's `HEALTHCHECK` has no
credentials to offer, and before the exemption existed, enabling auth marked
every deployment `unhealthy`. The exemption is an **exact path match** — a
prefix test would let `/healthz-anything` past the guard — and the route
discloses nothing (see below).

Startup prints the auth state either way, so an open instance is visible in the
container log rather than indistinguishable from a protected one:

```
Auth: HTTP Basic enabled for user 'david'
Auth: DISABLED — every endpoint is open, including file deletion and moves. …
```

Auth stays **off by default**: turning it on unconditionally would cut off every
LAN instance at its next restart.

### VR 180° detection (BL-121)

None of the sampled VR files carry spherical metadata (no `st3d`/`sv3d`), so the
server has only the file name to go on — `guess_vr_from_name()` matches `vr180`,
`180x180`, `3dh`, `sbs`, a standalone `lr`, and `oculus(-|_| )?rift`. A bare
`180` was tried and removed: it flagged ordinary files such as
"Episode 180 - The Long Goodbye.mkv" and recognised nothing the other patterns
had missed.

The second clue, a 2:1 aspect ratio, is checked **in the player**, not here: the
listing has no pixel dimensions, and obtaining them would mean one `ffprobe`
subprocess per entry on every folder open. The `<video>` element already knows
them by the time it matters.

Measured on a 24-file sample: the name alone recognises 15, the ratio covers the
rest. `vr_hint` (the guess) and `vr_mode` (the explicit choice) are both exposed
on video entries of `/api/files` and `/api/search`; the explicit choice always
wins, including `"off"` on a file the guess got wrong.

### API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/files?path=` | List folder contents |
| GET | `/api/progress?path=` | Read watch progress for a file |
| POST | `/api/progress?path=` | Save `{position, duration}` (clears the explicit watched flag) |
| POST | `/api/progress/watched?path=` | Set `{watched}` without playing the media; unmarking rewinds the position |
| DELETE | `/api/files?path=` | Delete a file or folder (drops progress/segments/tags of the entry and, for a folder, of everything below it) |
| POST | `/api/files/move?path=` | Move to `{destination}` (relative path), optional `{overwrite}` — starts a background job; **409** with `{code: "destination_exists", name, overwritable}` when the target is taken, `{code: "same_location"}` when it is the file's own place |
| POST | `/api/files/mkdir` | Create a folder `{path}` |
| POST | `/api/files/rename?path=` | Rename to `{new_name}` (base name only); migrates progress/segments/tags, including folder descendants |
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
| GET | `/healthz` | Liveness probe for the container `HEALTHCHECK`. **The only route reachable without credentials.** Checks the database and the media root; answers `{"status": "ok"}`, or `503` and `{"status": "error"}`. Says nothing else — no version, no paths, no counts. |
| GET | `/api/settings` | Read user settings |
| POST | `/api/settings` | Save user settings |
| POST | `/api/vr-mode?path=` | Remember how a file is rendered: `{mode: "off"\|"flat"\|"sbs"}` |
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
    cut_in REAL DEFAULT NULL,
    cut_out REAL DEFAULT NULL,
    watched INTEGER DEFAULT 0,   -- explicit state, wins over the position percentage
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

CREATE TABLE vr_modes (
    path       TEXT PRIMARY KEY,
    mode       TEXT NOT NULL,          -- "off" | "flat" | "sbs"
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
- `token` — optional. The bookmarklet download token (see below). Ignored when the caller already authenticates normally, which is the case for the Hoard UI itself.

**Response:**

```json
{ "job_id": "abc123" }
```

### Authentication (BL-011, BL-123)

Two mechanisms, both accepted by `require_basic_auth`, for two different callers.

**HTTP Basic** — opt-in via `HOARD_AUTH_USER` / `HOARD_AUTH_PASS`. Kept, not
replaced: dropping it would break `curl -u`, a future native client and any
external reader.

**Signed session cookie** — what a browser uses after the login screen.

| Aspect | Choice | Why |
|---|---|---|
| Contents | `{u, exp}` + HMAC-SHA256, base64url | Signed, not encrypted: neither field is a secret; what matters is that it cannot be forged. The signature is verified **before** the payload is parsed. |
| Key | `HOARD_SECRET_KEY`, else a `session_secret` row minted on first use | Explicit key ⇒ revocation by rotation. No key ⇒ a fresh install works with no configuration. |
| Lifetime | 30 days, reissued once less than half remains | Without sliding renewal, "30 days" means "30 days after the first login", which brings back the retyping the feature removes. |
| `SameSite` | `Lax` | **Not optional.** Basic credentials are never sent cross-site, so a third-party page could not trigger anything. A cookie would be — against an API exposing `DELETE /api/files` and `POST /api/files/move`. Lax is what closes that door. |
| `Secure` | `HOARD_COOKIE_SECURE`, default on | The backend is spoken to in plain HTTP behind the Synology reverse proxy, so it cannot detect HTTPS. A setting, not introspection. |
| `HttpOnly` | always | Keeps the cookie out of reach of any script on the page. |

**`WWW-Authenticate` is withheld from browsers**, in every request mode. While it
is sent, the browser opens its own credentials dialog and the in-app login screen
never appears.

`_looks_like_a_browser()` decides, on three signals of which any one is enough: a
`Sec-Fetch-*` header, `text/html` in `Accept`, or `Mozilla` in the `User-Agent`.
Testing `Accept: text/html` alone — the first version of this — was wrong in
exactly the case that mattered. Measured, per client:

| Client | `Accept` | `Sec-Fetch-Mode` |
|---|---|---|
| navigation | `text/html,…` | `navigate` |
| `fetch()` | `*/*` | `cors` |
| curl | `*/*` | *(absent)* |

A page's first act is `fetch('/api/settings')`, which is indistinguishable from
curl by `Accept` alone — so it got the challenge, and **Firefox pops its native
dialog on a fetch**. Chrome suppresses that dialog for fetch/XHR, which is why a
Chrome-only check missed it and the defect reached production.

The challenge is kept for non-browsers, though **no client here needs it**:
`curl -u` sends `Authorization` on the *first* request, without waiting to be
challenged. Waiting for a challenge is Digest behaviour, not Basic. An earlier
version of this document claimed the opposite and used it to justify the
`Accept`-based split.

**The app shell is served without credentials** (`SHELL_PATHS`: `/`,
`/index.html`, `/service-worker.js`, `/manifest.webmanifest`). This follows from
the line above: with no native dialog and the page behind the guard, an
unauthenticated browser would get a blank 401 and no way in at all. Every
`/api/*` route stays guarded, so no file, setting or listing is reachable — what
the shell exposes is the app's structure, which is already public (the repository
is public and `frontend/index.html` can be read there).

**Middleware order**: `/healthz`, `/api/login`, `/api/logout` and the shell pass
straight through; then the download-token routes; then a valid cookie; then valid
Basic; otherwise 401.

**Frontend.** `#login-screen` carries `gp-modal` and deliberately no
`data-gp-close`, so the pad drives it and **B** cannot dismiss it — the same rule
as the PIN lock. Two entry points raise it: `init()` treats the first
`GET /api/settings` as the session probe, and `apiFetch()` raises it on any 401.
On success the caller is resumed rather than the page reloaded, so the open folder
and the playing file survive. Note `#login-form input:focus:not(.gp-cursor)` in the
CSS: an id rule outranks `.gp-modal .gp-cursor`, so a plain `outline: none` on
focus would erase the pad cursor exactly when the pad lands on a field.

**The PIN is a separate thing** and stays that way: it is a screen lock on an
already-authenticated session, this decides whether the server answers at all.

### Bookmarklet Download Token (BL-124)

The bookmarklet POSTs to Hoard from whatever third-party page the user is on. That
request is cross-origin, so the browser attaches **neither** the Basic credentials
**nor** the session cookie — `SameSite` withholds the latter deliberately, and
widening it would reopen exactly the door the attribute exists to close. The
bookmarklet therefore carries a token of its own.

- **Storage**: a `download_token` row in `settings`, minted by
  `_get_or_create_download_token()` on first read of `GET /api/settings`.
  `POST /api/download/token/regenerate` mints a new one and the previous one stops
  working at once — that is the revocation mechanism.
- **Transport**: in the request **body**, never in the URL or query string. A
  credential in a URL ends up in the reverse proxy's access log and in the browser
  history.
- **Scope**: `POST /api/download` and `POST /api/download/status`, nothing else.
  It travels inside a bookmark clicked on arbitrary sites, so it must not be able
  to list, move or delete anything. Comparison is constant-time
  (`hmac.compare_digest`).

**Why these two routes bypass the blanket middleware.** `require_basic_auth` runs
*outside* `CORSMiddleware` (Starlette's `add_middleware` stacks last-added
outermost), so a 401 raised there carries no CORS headers whatsoever. The browser
discards such a response, and the caller only ever sees an opaque `TypeError:
Failed to fetch`. Worse, the **preflight** `OPTIONS` was answered the same way, so
the real POST was never even sent. The bookmarklet's `.catch` branch reported this
as a CSP problem — which is why the failure looked like a site incompatibility
rather than an authentication one. These two paths are listed in
`DOWNLOAD_TOKEN_PATHS` and authenticate themselves via `_require_download_auth()`,
so their 401 travels back out through `CORSMiddleware` and is readable by the
caller.

### Bookmarklet Progress (`POST /api/download/status`)

```json
{ "job_id": "abc123", "token": "…" }   →   { "status": "running", "progress": 42, "error": null }
```

A route of its own rather than a widened `GET /api/jobs`: the full job list would
hand any site the bookmark is clicked on the title, source URL and destination path
of every download. POST rather than GET so the token stays out of the URL.
Answers `404` for an unknown job id.

**Secrets in `settings`.** `GET /api/settings` returns the `settings` table
wholesale, so anything secret parked there ships to the frontend by default. The
`SECRET_SETTINGS` frozenset is the exclusion list; `pin_hash` is in it. The
download token is deliberately **not** — the frontend must read it to build a
working bookmarklet.

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

### Whole-interface side-by-side (PAD-SBS-UI)

XR glasses in 3D mode split the picture permanently, so the whole interface —
not just the player — has to be drawn once per eye. A toggle wraps everything
visible in `#app-root` and copies it into `#sbs-mirror`.

**Off costs nothing.** `#app-root { display: contents }` generates no box at
all, so the layout is byte-for-byte the one it had before the wrapper existed
(checked against the previous revision: every element's rect identical to the
hundredth of a pixel). `#sbs-mirror` is `display: none` and its shadow root is
emptied.

**The copy lives in a shadow root**, and that is load-bearing. Document-level
queries do not cross a shadow boundary, so `document.querySelectorAll('#filelist
.entry')` — which the pad cursor counts — and `.gp-modal` — which
`_gpOpenModal()` reads — keep answering with the originals alone. It also means
the ids can be kept inside the copy, which is what lets the page's own id-based
rules style it: the stylesheet is cloned into the shadow as is.

**A MutationObserver drives it, never a call at each render point.** BL-127
copied three windows from their three render functions because the three were
known; at the scale of the application a list filters, sorts and refreshes
itself during a download, and anything that requires each render point to be
declared will eventually miss one. A mirror frozen on a stale state is worse
than no mirror.

**Full copies are the fallback, patching is the routine.** A batch of mutations
is applied in place through a `WeakMap` from original element to copy;
`sbsCopy()` runs only on the first copy or when a batch cannot be applied.
Measured on a 2 000-entry folder (24 758 nodes):

| operation | cost |
|---|---|
| full copy (clone + insert) | ~50 ms |
| pad cursor step (patch) | 0.1 ms |
| sort / folder change (graft of the whole list) | ~70 ms, against ~26 ms without the mirror |
| scroll sync | ~20 ms, dominated by the copy's layout |

Two measurements shaped the design and are worth keeping in mind before
changing it. Reading `scrollTop` over every node cost **171 ms** on that folder —
each read makes the engine settle the layout again — so scroll containers are
found from the stylesheet (`sbsScrollSelector()`) instead of by walking.
And re-running the element queries every frame cost **30 ms per pad step**,
because the scroll selector ends in `[style*="overflow"]`, which no index can
answer; the pairs are therefore cached and rebuilt only when the copy is.

**What a clone does not carry** is transferred explicitly (BL-131): `value`,
`checked`, `selectedIndex`, a `<dialog>`'s open state and scroll positions.
Typing, ticking and scrolling produce no mutation at all, so `input`, `change`
and `scroll` are listened for in the capture phase. A password field's value is
never copied — only its length, as bullets.

**Pictures are repainted, not cloned** (BL-132). A cloned `<video>` plays
nothing and would mean a second download and a second decode; a cloned
`<canvas>` is blank, since a canvas's content is not in the DOM. Each `<video>`
becomes a `<canvas class="sbs-picture">` in the copy, and a rAF loop blits the
original into it — one download, one decode, one extra blit per frame. `<audio>`
and `<iframe>` are dropped. Verified in the network inspector: opening a video
or an image produces exactly one request.

**The VR canvas is the exception, and it is blitted from `_vrRender`.** A WebGL
canvas can only be read in the same task that drew it: once composited its buffer
is gone, unless the context is created with `preserveDrawingBuffer`, which costs
something on every frame whether the mirror is on or not. Copied from the generic
painter, the VR view came out as a black rectangle over the video — found by
review, not by the suite. `sbsBlitVr()` is therefore called at the end of
`_vrRender`, and the generic painter skips that pair.

**Real fullscreen is refused while the mode is on.** The fullscreen element goes
to the top layer, which ignores the transform that keeps each half's overlays
inside its half — the video would fill the whole screen, astride the split. Not a
corner case: the Deck has a touch screen, so `pointer: coarse` matches and the
pad's fullscreen button asks for the real one. `toggleFullscreen()` falls back to
the in-window kind.

**A 180° video is the one exception to "both eyes see the same picture".** That
rule is what makes the interface readable, and it holds for every screen and for
a flat video — but a 180° file *holds* two different pictures, one per eye, and
that difference is the relief. A first version coerced `setVrMode('sbs')` to
`'flat'` while the global mode was on, which showed the same eye twice and threw
the depth away; David reported it (relief with the screen mode off, none with it
on). `_vrRender` now detects `sbs && sbsIsOn()` and gives **a whole canvas to
each eye** instead of half a canvas to each: the right eye is drawn first and
blitted to the copy — a WebGL canvas is only readable in the task that drew it,
so the eye that goes to the copy must be the one in the buffer at that instant —
then the left eye is drawn over it and stays on screen. With one canvas per eye
nothing is stretched back, so `vr.sbsLayout` (auto/half/full) has nothing to act
on: the line leaves the pad menu and `cycleVrSbsLayout()` says so rather than
sitting inert. BL-127's per-window copies stay switched off, since the global
mirror already duplicates those windows.

**The toggle is device-local** — `localStorage['sbs_global']` — because the Deck
with the glasses wants it and the iPad must not inherit it, and because the PIN
screen is drawn before the settings are loaded.

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
