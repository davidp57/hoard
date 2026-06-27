# BL-070 — Barre de thumbnails (seek)

Status: ✅ done
Type: feat
Parent: FEAT-GALLERY ([PRD](../PRD.md))
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`

## What to build

Ajouter sous la visionneuse de galerie une barre de thumbnails qui sert de seek :
chaque vignette représente un élément de la séquence ; cliquer dessus saute à cet
index. Les vignettes sont générées à la volée par un nouvel endpoint
`/api/thumbnail?path=` qui downscale l'image via **ffmpeg** (pas de nouvelle
dépendance Python, **pas de cache**).

Le chargement est paresseux : seules les vignettes visibles dans la barre sont
demandées (au scroll). La première image principale de la galerie s'affiche
**immédiatement**, sans jamais attendre la génération des vignettes.

## Acceptance criteria

- [ ] `/api/thumbnail?path=` renvoie une vignette downscalée (200 + `Content-Type image/*`)
- [ ] `/api/thumbnail` rejette un chemin hors `MEDIA_ROOT` (path traversal)
- [ ] Une barre de thumbnails s'affiche sous la visionneuse de galerie
- [ ] Cliquer une vignette saute à l'index correspondant (seek)
- [ ] Les vignettes se chargent paresseusement (seules les visibles sont demandées)
- [ ] L'image principale s'affiche sans attendre les vignettes
- [ ] Tests API du endpoint thumbnail ; `ruff` + `pytest` au vert

## Blocked by

- BL-069 — Socle galerie-dossier lisible
