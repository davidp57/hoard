# BL-143 — Événements de lecture vers `progress`

Status: ⬜ ready
Lot: [FEAT-HERESPHERE](../PRD.md)

## Quoi

Chaque scène annonce `eventServer` = `…/heresphere/events`, et `POST /heresphere/events` reporte la position reçue dans `progress` (décision 6 du PRD).

## Critères d'acceptation

- [ ] Les événements 1 (lecture), 2 (pause) et 3 (fermeture) écrivent `time` / 1000 comme position du fichier désigné par `id` ; l'événement 0 (ouverture) ne change rien.
- [ ] Au-delà de `watched_threshold`, le fichier passe en « vu », comme depuis le lecteur web.
- [ ] `updated_at` suit : le fichier remonte dans « Récemment vus » et dans le tri « Vu » du web.
- [ ] Un `id` hors de `MEDIA_ROOT` ou inconnu est refusé sans rien écrire.
- [ ] Tests pytest : séquence ouverture → lecture → pause → fermeture, seuil « vu », refus hors racine.
- [ ] **Essai sur le Frame** : regarder une partie d'une vidéo dans FPX, la fermer, et la retrouver « en cours » au bon endroit dans Hoard sur le PC (David).
