# BL-003 — Marquer vu / non vu depuis la liste

Status: ✅ done
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`, `docs/user-guide.*.md`

## Problem

L'état « vu » ne s'obtient qu'en lisant réellement le fichier jusqu'au seuil. Le
ticket est à la roadmap depuis la v1.2 et `_gpToggleWatched()` existe déjà — mais
il exige `currentFile` **et** `video.duration`, donc ne fonctionne que dans le
player. Depuis la liste, un fichier jamais ouvert n'a pas de durée connue.

## Implementation Decisions

« Vu » est un **état**, pas une position. Les deux contournements possibles étaient
d'aller chercher la durée à `ffprobe` à chaque marquage (un processus externe pour
un clic, et un échec possible sur un fichier illisible), ou d'écrire
`position = duration = 1` — qui affiche « 0:01 / 0:01 » sous le nom et se fait
écraser dès la première lecture réelle. La table doit porter l'information.

## What to build

### Backend

- **Colonne `watched`** sur `progress` (`INTEGER DEFAULT NULL`), avec migration
  `PRAGMA table_info` + `ALTER TABLE` comme le reste du schéma. `NULL` = déduire du
  pourcentage (comportement actuel), `1` = vu, `0` = non vu explicitement.
- **`POST /api/progress/watched`** (`{watched: bool}`) : écrit l'état, crée la
  ligne si elle n'existe pas, et rafraîchit `updated_at` — un marquage manuel est
  un accès, il doit compter pour le tri « Vu » (BL-085).
- **`get_progress()` et `get_folder_state()`** consultent `watched` en priorité et
  ne retombent sur le pourcentage que s'il vaut `NULL`.
- Une lecture réelle qui franchit le seuil ne doit pas être contredite par un
  `watched = 0` oublié : sauvegarder une position **efface** l'état explicite.

### Frontend

- Action « Marquer vu / non vu » dans le menu contextuel (BL-086), section entrée.
- `_gpToggleWatched()` accepte une entrée de liste et passe par le nouvel endpoint
  quand aucune vidéo n'est ouverte.
- **Le player garde son chemin actuel** (écrire la position au seuil). Le faire passer
  par le nouvel endpoint, comme prévu initialement, se serait retourné contre le
  marquage : la sauvegarde automatique de position, toutes les 5 s puis à la
  fermeture, efface le drapeau explicite. Là où la durée est connue, écrire la
  position reste la façon durable de dire « vu ».
- Marquer ne s'applique qu'à un média ou à une galerie : un dossier ordinaire tire
  son état de son contenu, lui écrire une ligne de progression n'aurait pas de sens.

## Acceptance criteria

- [x] Marquer vu un fichier sans aucune ligne de progression le montre vu dans la liste
- [x] Marquer non vu un fichier lu à 100 % le montre non vu
- [x] Un dossier dont tous les fichiers sont marqués vus est `seen`
- [x] Reprendre la lecture efface l'état explicite
- [x] Un marquage manuel remonte l'entrée dans le tri « Vu »
- [x] La migration fonctionne sur une base créée sans la colonne
- [x] Marquer n'est proposé que sur un média ou une galerie
