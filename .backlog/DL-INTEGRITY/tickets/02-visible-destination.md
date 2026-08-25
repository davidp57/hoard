# BL-080 — Savoir où atterrissent les téléchargements

Status: ✅ done
Type: fix
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`

## What to build

Le réglage *Dossier de téléchargement* est un champ texte libre, et l'interface
n'en affiche que la valeur relative. Hoard crée le dossier s'il n'existe pas, en
silence. Résultat constaté en production : les téléchargements partaient dans un
dossier `[[_downloads` que l'utilisateur ne reconnaissait pas et ne savait pas
localiser sur le NAS.

### Backend

- `GET /api/settings` expose `download_folder_abs` : le chemin absolu résolu
  (`safe_path(download_folder)`), et `download_folder_exists`.
- Journaliser la création du dossier de destination quand elle a lieu :
  `logger.info("created download folder: %s", path)`.

### Frontend

- Modal de téléchargement : la ligne « Destination » affiche le **chemin complet**
  en plus du nom relatif.
- Réglages → Téléchargements : sous le champ, afficher le chemin absolu résolu et,
  quand le dossier n'existe pas encore, un avertissement « sera créé au premier
  téléchargement ».
- Bouton **« Parcourir… »** à côté du champ, réutilisant le sélecteur de dossiers
  existant (`openDestPicker`), pour choisir la destination par navigation plutôt
  qu'en saisie libre.

## Acceptance criteria

- [x] `GET /api/settings` renvoie `download_folder_abs` et `download_folder_exists`
- [x] Le modal de téléchargement affiche le chemin complet de destination
- [x] Les réglages affichent le chemin résolu et préviennent quand le dossier n'existe pas
- [x] Le sélecteur de dossiers permet de choisir la destination sans saisie libre
- [x] La création du dossier de destination est journalisée
- [x] `ruff check` + `ruff format --check` + `pytest` au vert
- [x] Docs utilisateur (FR + EN) à jour

## Blocked by

None — can start immediately

## Trouvé en chemin

`applyCfg()` recopie les réglages champ par champ côté client : les nouvelles clés
renvoyées par l'API restaient `undefined` dans `cfg`. `restart_supervised` était
dans ce cas depuis la v2.5.0 — la confirmation de redémarrage annonçait donc
toujours « aucun superviseur détecté », y compris en container. Corrigé avec
`media_root`, `download_folder_abs` et `download_folder_exists`.
