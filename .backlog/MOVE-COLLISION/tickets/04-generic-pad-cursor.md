# BL-093 — Curseur manette générique invisible

Status: 🔄 in-progress
Type: fix
Files: `frontend/index.html`, `docs/user-guide.*.md`

## What to build

BL-088 a donné au pad un parcours générique dans toutes les fenêtres sans
gestionnaire dédié, mais la classe `gp-cursor` qu'il pose n'avait de style que sur
`.entry`, `.modal-folder-btn` et les trois boutons de confirmation nommés. Dans les
huit autres fenêtres, le curseur bougeait **sans rien afficher** : l'utilisateur
appuyait sur A sans savoir sur quoi.

- Règle générique `.gp-modal .gp-cursor:not(.modal-folder-btn)` : contour à la
  couleur d'accent. Les cibles déjà stylées gardent la leur — les règles par `id` et
  `.modal-folder-btn` l'emportent.

## Acceptance criteria

- [x] Le curseur manette est visible dans la fenêtre d'écrasement
- [x] Les fenêtres tags, renommage, nouveau dossier, parcourir, sélecteur de
      destination, file d'attente et code PIN en profitent sans retouche
- [x] Les fenêtres déjà stylées (déplacement, export) sont inchangées
