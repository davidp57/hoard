# BL-042 — Transcodage matériel optionnel (VAAPI / NVENC)

Status: ⬜ ready
Type: feat
Files: `backend/main.py` (ou `backend/stream.py` après BL-041), `docker-compose.yml`, `docs/developer.en.md`

## What to build

Ajouter une variable d'env `FFMPEG_HW_ACCEL` (`vaapi`, `nvenc`, vide = software). Quand
définie, injecter les flags d'encodeur matériel appropriés dans la commande ffmpeg de
transcodage. Documenter l'exposition de `/dev/dri` dans `docker-compose.yml` pour
Synology. Si le device est indisponible au démarrage, logger un warning et retomber
silencieusement sur l'encodage software.

## Acceptance criteria

- [ ] `FFMPEG_HW_ACCEL` pilote l'encodeur (vaapi / nvenc / software par défaut)
- [ ] Device absent → warning + fallback software, jamais d'échec dur
- [ ] Le chemin software par défaut reste inchangé (100 % opt-in)
- [ ] `docker-compose.yml` documente l'exposition `/dev/dri`
- [ ] Doc developer (env var) à jour ; `ruff` + `pytest` au vert

## Blocked by

None — recommandé après BL-041 (les flags atterrissent dans `stream.py`)
