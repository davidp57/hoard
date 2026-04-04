# MediaBrowser

Web video browser with watch-progress tracking, designed for a Synology NAS.

[![CI](https://github.com/YOUR_USER/nas-vid-bro/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USER/nas-vid-bro/actions/workflows/ci.yml)

## Features

- 📁 Raw filesystem browser (no library, no metadata)
- ▶️ Integrated HTML5 player — seek, volume, touch gestures
- 💾 Auto-save position every 5 s, resume on re-open
- 🟡 Visual status in file list: unseen / in-progress (% + bar) / watched (≥ 90 %)
- ↗️ Move to predefined folders (quick modal)
- 🗑️ Delete files/folders with confirmation
- 👆 Touch: swipe-seek, swipe-volume, double-tap ±10 s
- ⌨️ Keyboard: Space, ←→ seek ±10 s, ↑↓ volume

## Project structure

```
.
├── backend/
│   ├── main.py              # FastAPI app (all backend logic)
│   └── requirements.txt
├── frontend/
│   └── index.html           # Single-file UI (vanilla HTML/CSS/JS)
├── tests/
│   ├── conftest.py          # Pytest fixtures + temp env setup
│   └── test_api.py          # API endpoint tests (31 cases, 99 % coverage)
├── .github/workflows/
│   ├── ci.yml               # Lint + test on every push/PR
│   └── docker-build.yml     # Docker image build on main / tags
├── docker-compose.yml       # Production (Synology)
├── docker-compose.dev.yml   # Development override (hot-reload)
├── Dockerfile
├── pyproject.toml           # Pytest + ruff config
├── requirements-dev.txt
└── ROADMAP.md
```

## Quick start (local)

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run with a local media folder
export MEDIA_ROOT=/path/to/videos
export PREDEFINED_FOLDERS="Vu,A revoir"
export DB_PATH=/tmp/progress.db

uvicorn backend.main:app --reload --port 8000
# → http://localhost:8000
```

## Development with Docker (hot-reload)

```bash
# Create a local media folder first
mkdir dev-media

docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
# → http://localhost:8000
# Backend reloads automatically on save.
# Override media path: LOCAL_MEDIA_PATH=/your/path docker compose ...
```

## Tests

```bash
python -m pytest tests/ -v
```

Coverage report is written to `coverage.xml`.

## Deployment on Synology

1. Copy the project folder to `/volume1/docker/mediabrowser/`
2. Edit `docker-compose.yml` — set the correct media volume path
3. Run:

```bash
docker compose up -d --build
# → http://NAS_IP:8000
```

See [ROADMAP.md](ROADMAP.md) for planned features.
- Adapte le chemin du volume
- Deploy

## Configuration

Toute la config passe par les variables d'environnement dans `docker-compose.yml` :

| Variable | Défaut | Description |
|---|---|---|
| `MEDIA_ROOT` | `/media` | Chemin racine des médias dans le container |
| `PREDEFINED_FOLDERS` | `Vu,A revoir,A supprimer` | Dossiers cibles pour le déplacement rapide (séparés par des virgules) |
| `DB_PATH` | `/data/progress.db` | Chemin de la base SQLite |

## Développement local

```bash
cd mediabrowser
pip install -r backend/requirements.txt

# Pointe sur un vrai dossier vidéo
export MEDIA_ROOT=/chemin/vers/tes/videos
export PREDEFINED_FOLDERS="Vu,A revoir"
export DB_PATH=/tmp/progress.db

uvicorn backend.main:app --reload --port 8000
```

Puis ouvre `http://localhost:8000`
