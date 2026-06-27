# BL-013 — Thème clair (toggle)

Status: ⬜ ready
Type: feat
Files: `frontend/index.html`

## What to build

Ajouter un thème clair commutable depuis l'UI, persisté en `localStorage`
(device-local, comme `volume`). Les couleurs sont déjà centralisées dans `:root` ;
introduire un jeu de tokens clairs (p. ex. via un attribut `data-theme="light"` sur
`<html>` ou `<body>`) et un bouton de bascule. Garder la cohérence visuelle sur les
trois états : liste, player, et overlays/dialogs.

## Acceptance criteria

- [ ] Un contrôle permet de basculer sombre ↔ clair depuis l'UI
- [ ] Le choix est persisté en `localStorage` et restauré au chargement
- [ ] Tous les tokens de couleur passent par `:root` (aucune couleur en dur)
- [ ] Liste, player et dialogs/overlays restent lisibles et cohérents en thème clair
- [ ] Syntaxe JS validée (`node --check`)

## Blocked by

None — can start immediately (branche `feature/light-theme` déjà existante)
