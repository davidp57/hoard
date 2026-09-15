# BL-091 — Métadonnées des dossiers : descendants et tags

Status: 🔄 in-progress
Type: fix
Files: `backend/main.py`, `tests/test_api.py`, `docs/developer.en.md`

## What to build

- **`_purge_paths(conn, rel)`** : supprime les lignes `progress`, `segments` et
  `file_tags` du chemin **et de tous ses descendants** (comparaison par `substr`, pas
  `LIKE`, pour que `_` et `%` dans un nom ne soient pas des jokers).
- **`_migrate_renamed_paths`** migre aussi `file_tags`, entrée et descendants.
- **`DELETE /api/files`** passe par `_purge_paths` : supprimer un dossier laissait
  les métadonnées de tout son contenu, et les tags n'étaient purgés nulle part.
- **`_run_move`** migre par la même fonction, donc un dossier déplacé emporte la
  progression et les tags de son contenu.
- **`rename_path`** purge la destination avant de migrer dessus : son garde
  `dest.exists()` ne voit pas une ligne orpheline, et migrer `file_tags` l'exposait
  au même `IntegrityError` que le déplacement.

## Acceptance criteria

- [x] Un dossier déplacé conserve la progression et les tags de ses fichiers
- [x] Supprimer un dossier purge les métadonnées de tout son contenu
- [x] Renommer conserve les tags comme il conservait déjà la progression
- [x] Renommer par-dessus une ligne orpheline ne rend plus 500
