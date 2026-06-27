# BL-072 — Passagers (fichiers non-image dans une galerie)

Status: ⬜ ready
Type: feat
Parent: FEAT-GALLERY ([PRD](../PRD.md))
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`

## What to build

Gérer les **passagers** : un fichier non-image présent dans un dossier-galerie (PDF,
texte, audio, archive) ne casse pas la galerie et n'est pas caché. `/api/gallery/list`
l'inclut dans la séquence à sa position d'ordre, avec son type. Il occupe un index
comme une image : la visionneuse l'atteint en navigation et affiche son aperçu.

Aperçus rendus **côté client** : PDF → 1ʳᵉ page via PDF.js (déjà bundlé) ; txt →
extrait des premières lignes. Pour les autres types (audio, archive) en v1 : vignette
et affichage par icône générique + nom. La vignette du passager dans la barre suit la
même logique (aperçu PDF/txt, sinon icône).

## Acceptance criteria

- [ ] `/api/gallery/list` inclut les passagers à leur position d'ordre avec leur type
- [ ] Un passager occupe un index dans la séquence (atteint en prev/next)
- [ ] Aperçu PDF (1ʳᵉ page) et txt (extrait) rendus côté client dans la visionneuse
- [ ] Audio/archive affichés par icône générique + nom en v1
- [ ] La vignette du passager dans la barre reflète l'aperçu (PDF/txt) ou une icône
- [ ] Tests API : présence et type des passagers dans `/api/gallery/list`
- [ ] `ruff` + `pytest` au vert

## Blocked by

- BL-070 — Barre de thumbnails (seek)
