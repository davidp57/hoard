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

### Path Safety

Every file access goes through `safe_path(rel_path)`, which verifies the resolved path stays under `MEDIA_ROOT`. Any path traversal attempt returns a 400 error.

```python
def safe_path(rel: str) -> Path:
    resolved = (MEDIA_ROOT / rel).resolve()
    if not str(resolved).startswith(str(MEDIA_ROOT.resolve())):
        raise HTTPException(400, "Invalid path")
    return resolved
```

### API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/files?path=` | List folder contents |
| GET | `/api/progress?path=` | Read watch progress for a file |
| POST | `/api/progress?path=` | Save `{position, duration}` |
| DELETE | `/api/files?path=` | Delete a file or folder |
| POST | `/api/files/move?path=` | Move to `{destination}` (relative path) |
| POST | `/api/files/mkdir` | Create a folder `{path}` |
| POST | `/api/files/cut` | Cut video via ffmpeg `{path, start, end, output}` |
| GET | `/api/jobs` | Status of ongoing background jobs (ffmpeg cuts, downloads) |
| GET | `/api/quick-folders` | List pinned folders |
| POST | `/api/quick-folders` | Pin a folder `{path}` |
| DELETE | `/api/quick-folders?path=` | Unpin a folder |
| GET | `/api/browse?path=` | Browse the directory tree (used by the move modal) |
| GET | `/api/settings` | Read user settings |
| POST | `/api/settings` | Save user settings |
| GET | `/api/stream?path=` | HTTP video stream with `Range` support (native seeking) |
| GET | `/api/transcode?path=` | Transcoded stream via ffmpeg |
| POST | `/api/download` | Download a web video via yt-dlp `{url, cookies?}` |

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
```

### ffmpeg Jobs

Video cuts (`/api/files/cut`) and web downloads (`/api/download`) run in background daemon threads. Each job's status is held in memory in a `jobs: dict[str, JobStatus]` dict. The `/api/jobs` endpoint lets the frontend poll for progress.

### Download Endpoint (`POST /api/download`)

**Request body** (`DownloadRequest`):

```json
{ "url": "https://example.com/video", "cookies": "name=value; other=foo" }
```

- `url` — required. The web page or direct video URL.
- `cookies` — optional. Raw `document.cookie` string captured by the bookmarklet. Converted to Netscape format and passed to yt-dlp.

**Response:**

```json
{ "job_id": "abc123" }
```

**Security (SSRF protection):** The endpoint rejects `file://` URLs and any host that resolves to localhost or RFC-1918 private addresses (`127.*`, `::1`, `192.168.*`, `10.*`, `172.*`).

**Cookie resolution order:**
1. Persistent `cookies.txt` file (path from `download_cookies_path` setting), if it exists.
2. Inline cookies from the request body, written to a temporary file.

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
