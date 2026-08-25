# Hoard — Installation Guide

## Prerequisites

| Method | Requirements |
|--------|-------------|
| Local (Python) | Python 3.12+, pip, ffmpeg (for video trimming and downloads) |
| Docker | Docker Engine 24+, Docker Compose v2 |
| Synology NAS | DSM 7+, Docker or Container Manager package |

> **Note:** `yt-dlp` is automatically installed as a Python dependency (`requirements.txt`). `ffmpeg` must be available on the system PATH for video trimming and for merging audio/video streams during downloads. The Docker image includes both.

---

## 1. Local Installation (Python)

### Clone the repository

```bash
git clone https://github.com/davidp57/hoard.git
cd hoard
```

### Create the virtual environment and install dependencies

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements-dev.txt
```

### Run the application

```bash
# Required environment variables
export MEDIA_ROOT=/path/to/your/videos   # folder to browse
export DB_PATH=/tmp/hoard.db             # SQLite database
export PREDEFINED_FOLDERS="Watched,To review"  # quick folders (optional)

uvicorn backend.main:app --reload --port 8000
```

On Windows PowerShell, replace `export` with `$env:`:

```powershell
$env:MEDIA_ROOT = "C:\Videos"
$env:DB_PATH = "$env:TEMP\hoard.db"
uvicorn backend.main:app --reload --port 8000
```

Open `http://localhost:8000` in your browser.

---

## 2. Docker (Local Development)

### Prepare the media folder

```bash
mkdir dev-media
# Copy a few video files into dev-media/ for testing
```

### Run with hot-reload

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

The backend reloads automatically on every change to `backend/main.py`.  
To point to an external media folder:

```bash
LOCAL_MEDIA_PATH=/absolute/path/to/videos \
  docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

---

## 3. Production Deployment (Synology NAS)

### Copy files to the NAS

Via SSH or the DSM File Station, copy the repository contents to:

```
/volume1/docker/hoard/
```

### Adjust docker-compose.yml

Open `docker-compose.yml` and update the media volume path:

```yaml
volumes:
  - /volume1/downloads:/media:rw   # adjust this path
  - hoard_data:/data
```

### Start the container

```bash
# On the NAS via SSH
cd /volume1/docker/hoard
docker compose up -d --build
```

The application will be available at `http://NAS_IP:8000`.

### Updating

```bash
docker compose pull
docker compose up -d
```

---

## 4. Configuration

All configuration is done via **environment variables** in `docker-compose.yml` (under the `environment` key) or when starting the server directly.

| Variable | Default | Description |
|----------|---------|-------------|
| `MEDIA_ROOT` | `/media` | Media root path inside the container |
| `DB_PATH` | `/data/progress.db` | SQLite watch-progress database |
| `PREDEFINED_FOLDERS` | `Vu,A revoir,A supprimer` | Quick folders (comma-separated) |
| `SSL_CERTFILE` | *(unset)* | Path to a PEM certificate file. Enables native HTTPS — no reverse proxy needed. |
| `SSL_KEYFILE` | *(unset)* | Path to the matching PEM private key file. |
| `HOARD_AUTH_USER` / `HOARD_AUTH_PASS` | *(unset)* | Set both to require HTTP Basic auth on every request. Recommended when exposing Hoard outside your LAN. Use HTTPS so credentials are not sent in clear text. |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `LOG_DIR` | `<DB_PATH directory>/logs` | Directory holding the log files. Empty string disables file logging (stdout only). |
| `LOG_RETENTION_DAYS` | `30` | Number of daily log files kept (rotation at midnight). |
| `RESTART_SUPERVISED` | *(auto-detected)* | `0` / `1`. Whether a supervisor restarts the process after it exits. Auto-detected inside a container; only used to word the "Restart Hoard" confirmation. |
| `JOB_TTL_SECONDS` | `3600` | How long a finished job stays in memory. Does not affect the download history, which lives in the database. |
| `DOWNLOAD_SOCKET_TIMEOUT` | `30` | Seconds of silence tolerated on a download socket before giving up. Stops a silent server from pinning the (sequential) queue. |

### Enabling HTTPS

To serve Hoard over HTTPS without a reverse proxy, generate a certificate and set the two env vars:

```bash
# Self-signed cert (valid 10 years)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
  -days 3650 -nodes -subj "/CN=nas.local"
```

Or use [mkcert](https://github.com/FiloSottile/mkcert) for a locally-trusted cert:
```bash
mkcert nas.local
```

Then in `docker-compose.yml`:
```yaml
volumes:
  - /path/on/nas/certs:/certs:ro
environment:
  - SSL_CERTFILE=/certs/cert.pem
  - SSL_KEYFILE=/certs/key.pem
```

The application will be available at `https://NAS_IP:8000`.

This also enables PWA installability on real devices: service workers and standalone install prompts require HTTPS (or `localhost` during local development).

### Using Portainer

In the Portainer UI, create a stack from `docker-compose.yml` content and adjust environment variables to match your setup.

---

## 5. Reverse Proxy (External Access)

To expose Hoard via a subdomain (e.g. `hoard.mynas.me`), use the DSM built-in reverse proxy:

1. **Control Panel → Login Portal → Reverse Proxy**
2. Add a rule:
   - Source: `hoard.mynas.me:443` (HTTPS)
   - Destination: `localhost:8000`

> **Warning:** if you expose the app outside your LAN, enable authentication first (see v2.0 roadmap).

---

## 6. Data Persistence

The SQLite database (`progress.db`) stores watch progress for all files, plus the **download history**. It is mounted in a named Docker volume (`hoard_data`) so it survives container updates.

### Logs

Logs are written **both** to stdout (visible in Portainer) and to a `hoard.log` file placed next to the database by default — `/data/logs/hoard.log` with the standard configuration, so **inside the same persistent volume**. The file rotates every night and **30 days** are kept (`LOG_RETENTION_DAYS`).

They can be read from the UI: **Settings → Maintenance → Log**. Logs contain downloaded URLs and caller IP addresses; if Hoard is reachable outside your LAN, protect it with `HOARD_AUTH_USER` / `HOARD_AUTH_PASS`.

To pull the logs out to the host:

```bash
docker run --rm -v hoard_data:/data -v $(pwd):/backup alpine cp -r /data/logs /backup/hoard-logs
```

To back up / export the database:

```bash
docker run --rm \
  -v hoard_data:/data \
  -v $(pwd):/backup \
  alpine cp /data/progress.db /backup/progress.db.bak
```
