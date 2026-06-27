# BL-073 — Unification archive↔galerie & finitions

Status: ⬜ ready
Type: feat
Parent: FEAT-GALLERY ([PRD](../PRD.md))
Files: `frontend/index.html`, `docs/user-guide.en.md`, `docs/user-guide.fr.md`, `docs/developer.en.md`, `docs/developer.fr.md`, `CHANGELOG.md`, `docs/changelog-user.fr.md`

## What to build

Faire converger les deux supports de galerie vers une expérience unique. La lecture
d'archive (`openArchive`) réutilise la logique de visionneuse galerie commune : barre
de thumbnails, même icône 🖼️ dans la liste (dossier comme archive), même jeu de
commandes (clavier/pad/gestes, plein écran). Seule la source des images diffère
(archive vs dossier).

Finaliser le plein écran et les gestes tactiles sur la galerie, puis la documentation :
guides utilisateur EN/FR, doc developer (nouveaux endpoints `/api/gallery/list` et
`/api/thumbnail`, concept galerie), `CHANGELOG.md` et `docs/changelog-user.fr.md`.

## Acceptance criteria

- [ ] L'archive utilise la même visionneuse galerie (barre de thumbnails comprise)
- [ ] Icône 🖼️ pour les galeries-archives comme pour les galeries-dossiers
- [ ] Plein écran et gestes tactiles fonctionnent sur une galerie
- [ ] user-guide EN/FR mis à jour (lecture d'un dossier d'images, barre de thumbnails)
- [ ] developer EN/FR documente les nouveaux endpoints et le concept galerie
- [ ] `CHANGELOG.md` + `docs/changelog-user.fr.md` à jour
- [ ] `ruff` + `pytest` au vert ; syntaxe JS validée (`node --check`)

## Blocked by

- BL-070 — Barre de thumbnails (seek)
- BL-071 — Gestion d'image & actions galerie
- BL-072 — Passagers (fichiers non-image dans une galerie)
