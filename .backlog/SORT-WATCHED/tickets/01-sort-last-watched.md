# BL-085 — Tri « Vu » par date de dernier visionnage

Status: ✅ done
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`, `docs/user-guide.*.md`

## What to build

### Backend

- **`_last_watched_index(conn)`** : lit `path` + `CAST(strftime('%s', updated_at) AS
  INTEGER)` depuis `progress`, et pour chaque ligne remonte la chaîne des dossiers
  parents en conservant le maximum. Rend un `dict` chemin relatif → epoch couvrant
  aussi bien les médias que tous leurs ancêtres.
- **Champ `last_watched`** ajouté à chaque entrée de `/api/files` et `/api/search`,
  à `0` quand rien n'a jamais été regardé dessous.
- `sort_by` accepte la valeur `'watched'`.

### Frontend

- Bouton **Vu** dans la barre de tri + option « Vu récemment » dans
  **Paramètres → Tri par défaut**.
- Branche `sortBy === 'watched'` dans `sortedList()` : tri sur `last_watched`, les
  entrées à `0` renvoyées en fin de liste quel que soit le sens, départagées par
  `mtime`.

## Acceptance criteria

- [x] Un média regardé à deux niveaux de profondeur fait remonter son dossier de tête
- [x] Le dossier intermédiaire porte la même date que le dossier de tête
- [x] Un fichier porte sa propre date de visionnage
- [x] Un dossier voisin jamais regardé reste à `0`
- [x] Les résultats de recherche exposent le champ
- [x] Le tri « Date » existant est inchangé
