# Lot GAMEPAD-FIXES — Correctifs gamepad post-recette ✅

Status: ✅ done
Terminé: 2026-05-15

**Goal**: Stabiliser le support gamepad après recette : dialogs visibles en plein écran,
machine à états du move-dialog, anti-inputs parasites, préservation du curseur.

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-043 | Préservation du curseur après action fichier (`_gpPendingRestoreIdx`) | fix | ✅ |
| BL-044 | Cooldown `_gpActionCooldown` (600 ms) anti-inputs parasites post-dialog | fix | ✅ |
| BL-045 | Machine à états 2 phases pour `move-dialog` (folders → confirm) | fix | ✅ |
| BL-046 | `delete-dialog` / `move-dialog` en overlay, déplacés dans le fullscreen | fix | ✅ |
| BL-052 | Régression BL-043 : index restauré avant le `renderFiles` final (auto-play) | fix | ✅ |
