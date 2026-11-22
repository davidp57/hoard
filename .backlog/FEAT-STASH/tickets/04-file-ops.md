# BL-150 — Déplacer et supprimer dans le dossier de Stash

Status: ✅ done
Lot: [FEAT-STASH](../PRD.md)

## Quoi

Décision 7 du PRD : dans `stash_folder`, Hoard passe par Stash pour que Stash garde ses métadonnées.

## Critères d'acceptation

- [x] Déplacement ou renommage qui reste dans le dossier : `moveFiles` ; `progress` suit le fichier comme aujourd'hui.
- [x] Suppression dans le dossier : `sceneDestroy(delete_file: true, delete_generated: true)`.
- [x] Déplacement qui sort du dossier : déplacement disque habituel, puis `sceneDestroy` sans `delete_file`.
- [x] Dossier entier déplacé ou supprimé : même règle pour chaque vidéo qu'il contient.
- [x] Stash injoignable ou réglage absent alors que le dossier existe : refus clair, rien ne bouge.
- [x] Tests pytest avec le faux Stash pour chaque cas.
- [x] Doc : guide utilisateur FR + EN (ce qui se passe dans le dossier de Stash) ; doc développeur.
