# BL-090 — Destination occupée : choix écraser / annuler

Status: 🔄 in-progress
Type: fix
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`, `docs/user-guide.*.md`, `docs/developer.en.md`

## What to build

### Backend

- **`move_target(source, destination)`** : où la source atterrit réellement — dans
  `destination` quand c'est un dossier existant, à `destination` sinon. Partagée par
  l'endpoint et le job, sans quoi le contrôle porterait sur un autre chemin que le
  déplacement.
- **`MoveRequest.overwrite`** (défaut `False`).
- **`POST /api/files/move`** répond **409** avant de lancer le job :
  - `{"code": "same_location"}` si la destination est la place actuelle du fichier ;
  - `{"code": "destination_exists", "name": ..., "overwritable": ...}` si elle est
    occupée et que `overwrite` n'est pas demandé. `overwritable` est vrai seulement
    pour un fichier déplacé sur un fichier.
- **`_run_move`** revérifie la destination (le job tourne plus tard), purge les
  lignes de métadonnées qui s'y trouvent, migre celles de la source, met le fichier
  remplacé de côté (`.<nom>.hoard-replaced-<hex>`) avant le déplacement, puis
  l'efface au succès ou le remet en place à l'échec.
- Le déplacement post-export (`_run_export`, `_run_export_segments`) refuse une
  destination occupée et le signale dans `move_error` au lieu d'écraser.

### Frontend

- **`requestMove(sourcePath, destPath)`** : poste le déplacement, traite le 409 et
  relance avec `overwrite: true` après accord. Utilisée par les deux chemins de
  déplacement (dossiers épinglés et sélecteur libre).
- **Fenêtre `#overwrite-dialog`** : Écraser / Annuler, `gp-modal` +
  `data-gp-close="closeOverwriteDialog"` pour le parcours manette et clavier,
  curseur initial sur **Annuler**, `Échap` et clic sur le fond équivalents à Annuler.

## Acceptance criteria

- [x] Un fichier du même nom à destination ouvre la fenêtre au lieu de planter
- [x] « Écraser » remplace le fichier et la progression devient celle du fichier déplacé
- [x] « Annuler » ne déplace rien et ne touche à aucune métadonnée
- [x] Une ligne `progress` orpheline à la destination ne bloque plus le déplacement
- [x] Un dossier à destination n'est pas proposé à l'écrasement
- [x] Déplacer un fichier vers son propre dossier est refusé proprement
- [x] La fenêtre se pilote entièrement à la manette (D-pad, A, B) et au clavier
- [x] Annuler laisse le lecteur ouvert : le fichier n'est relâché qu'une fois le
      déplacement lancé, la reprise sur `PermissionError` couvrant le verrou Windows
