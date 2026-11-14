# BL-143 — Événements de lecture vers `progress`

Status: 🧑 waiting-human
Lot: [FEAT-HERESPHERE](../PRD.md)

## Quoi

Chaque scène annonce `eventServer` = `…/heresphere/events`, et `POST /heresphere/events` reporte la position reçue dans `progress` (décision 6 du PRD).

## Critères d'acceptation

- [x] Les événements 1 (lecture), 2 (pause) et 3 (fermeture) écrivent `time` / 1000 comme position du fichier désigné par `id` ; l'événement 0 (ouverture) ne change rien.
- [x] Au-delà de `watched_threshold`, le fichier passe en « vu », comme depuis le lecteur web.
- [x] `updated_at` suit : le fichier remonte dans « Récemment vus » et dans le tri « Vu » du web.
- [x] Un `id` hors de `MEDIA_ROOT` ou inconnu est refusé sans rien écrire.
- [x] Tests pytest : séquence ouverture → lecture → pause → fermeture, seuil « vu », refus hors racine.
- [ ] **Essai sur le Frame** : regarder une partie d'une vidéo dans FPX, la fermer, et la retrouver « en cours » au bon endroit dans Hoard sur le PC (David).

## Réalisation (2026-11-14)

- L'événement ne porte pas de durée : elle vient de `progress`, sinon d'un ffprobe mis en cache. Sans durée lisible, la position est écrite seule (durée 0, pas de « vu »).
- `watched` passe à 1 au-delà de `watched_threshold`, à 0 en dessous, comme une sauvegarde du lecteur web remet le drapeau à zéro.
