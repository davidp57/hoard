# BL-071 — Gestion d'image & actions galerie

Status: ⬜ ready
Type: feat
Parent: FEAT-GALLERY ([PRD](../PRD.md))
Files: `frontend/index.html`, `backend/main.py`, `tests/test_api.py`

## What to build

Distinguer les deux granularités d'action sur une galerie :

- **Image isolée (souris, desktop)** : au survol d'une vignette de la barre de
  thumbnails, deux icônes apparaissent — X (supprimer cette image) et `>` (déplacer
  cette image via le picker de destination existant). Action considérée comme rare,
  desktop/souris uniquement (pas de survol sur tactile).
- **Galerie entière (clavier/pad)** : les raccourcis delete/move dans la visionneuse
  agissent sur le dossier-galerie entier, comme pour une vidéo. Le marquage manuel
  vu/non-vu (`W`) s'applique à la galerie. En plein écran, supprimer/déplacer la
  galerie enchaîne automatiquement sur l'élément suivant du dossier parent (comme une
  vidéo).

Supprimer/déplacer une image met à jour la séquence et l'index courant. Pas
d'auto-enchaînement vers l'élément suivant à la fin d'une galerie (on s'arrête sur la
dernière image, galerie passée « vue »).

## Acceptance criteria

- [ ] Survol d'une vignette → icônes X et `>` (desktop) ; supprimer/déplacer l'image agit sur ce seul fichier
- [ ] Après suppression/déplacement d'une image, la séquence et l'index courant restent cohérents
- [ ] Raccourcis clavier/pad delete/move dans la visionneuse → agissent sur la galerie entière
- [ ] `W` marque la galerie vue / non-vue
- [ ] En plein écran, delete/move de la galerie enchaîne sur l'élément suivant du parent
- [ ] Pas d'auto-enchaînement à la fin d'une galerie ; la dernière image passe la galerie « vue »
- [ ] `ruff` + `pytest` au vert (déplacement/suppression d'image couverts côté API si endpoint impacté)

## Blocked by

- BL-070 — Barre de thumbnails (seek)
