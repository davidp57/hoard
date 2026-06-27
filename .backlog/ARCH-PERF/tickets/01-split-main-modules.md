# BL-041 — Découpage de `main.py` en modules ciblés

Status: ⬜ ready
Type: chore
Files: `backend/main.py`, `backend/config.py`, `backend/db.py`, `backend/stream.py`, `backend/download.py`

## What to build

Extraire trois modules frères de `backend/main.py`, en gardant `main.py` comme point
d'entrée FastAPI (~600–800 lignes) :

- `backend/db.py` — `init_db`, `get_db`, migrations inline
- `backend/stream.py` — endpoint de streaming, pipeline ffmpeg/transcode
- `backend/download.py` — file yt-dlp, dict `_jobs`, endpoints de download

Définir les globals partagés (`MEDIA_ROOT`, `FFMPEG_BIN`, `FFPROBE_BIN`) dans
`backend/config.py` et les importer de là pour éviter les imports circulaires.
Aucun changement de comportement.

## Acceptance criteria

- [ ] `main.py` réduit à l'entrée FastAPI + câblage des routes
- [ ] `db.py` / `stream.py` / `download.py` / `config.py` créés et cohérents
- [ ] Aucun import circulaire
- [ ] Tous les tests existants passent **sans modification**
- [ ] `ruff check` + `ruff format --check` au vert

## Blocked by

None — can start immediately
