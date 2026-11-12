# BL-113 — Galerie d'images et archives

Status: ⬜ ready
Type: feat
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 03
Files: `client/lib/`

## What to build

Les galeries : un dossier d'images se lit comme un média unique avec reprise,
de même qu'une archive `.cbz` / `.cbr` / `.zip` (voir ADR 0002 et lot
FEAT-GALLERY). Routes `/api/gallery/list`, `/api/archive/list`,
`/api/archive/image`, `/api/thumbnail`.

Attention : le pont de rendu mis en cause pour la vidéo (BL-109) sert aussi ici
si les images passent par une texture. Vérifier que le défilement d'images
n'hérite pas du même défaut de rafraîchissement.

## Acceptance criteria

- [ ] Un dossier-galerie et une archive se lisent avec reprise
- [ ] Barre de vignettes servant de navigation
- [ ] Défilement fluide, mesuré et non supposé
