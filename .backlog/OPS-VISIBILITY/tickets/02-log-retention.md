# BL-076 — Journalisation fichier avec rétention de 30 jours

Status: ✅ done
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/conftest.py`, `tests/test_api.py`, `docs/installation.*.md`, `docs/developer.en.md`

## What to build

Conserver 30 jours de logs sur le volume persistant, et les rendre consultables
depuis l'interface.

### Backend

- Dans le bloc `── Logging ──` de `backend/main.py`, ajouter un
  `TimedRotatingFileHandler` à côté du handler stdout existant :
  - fichier : `<LOG_DIR>/hoard.log`
  - rotation : `when="midnight"`, `backupCount=LOG_RETENTION_DAYS`
  - même format que stdout
- Variables d'environnement :
  - `LOG_DIR` — défaut `<dossier de DB_PATH>/logs`, donc `/data/logs` en production
    (volume `hoard_data` déjà monté, aucun changement de `docker-compose.yml`
    nécessaire). Chaîne vide = pas de fichier, stdout seul.
  - `LOG_RETENTION_DAYS` — défaut `30`.
- stdout reste actif : les logs Docker / Portainer continuent de fonctionner.
- Création du dossier au démarrage ; si elle échoue (droits, volume en lecture
  seule), journaliser un warning sur stdout et continuer sans fichier — jamais
  d'échec de démarrage à cause des logs.
- `GET /api/logs?lines=500&level=` — renvoie les N dernières lignes du fichier
  courant (lecture par la fin, sans charger tout le fichier). `level` filtre
  optionnel sur le niveau. Renvoie une liste vide et un indicateur explicite quand
  la journalisation fichier est désactivée.

### Frontend

- Réglages → nouvelle section **Maintenance** → « Journal ».
- Zone de consultation en police à chasse fixe, en **ordre chronologique** avec
  défilement automatique en bas (inverser ligne à ligne casserait les traces
  d'erreur multi-lignes), avec : sélecteur du nombre de lignes (100 / 500 / 2000),
  filtre de niveau, bouton d'actualisation, et copie dans le presse-papier.
- Message clair quand les logs fichier sont désactivés.

## Acceptance criteria

- [x] Les logs sont écrits dans `<LOG_DIR>/hoard.log` en plus de stdout
- [x] Rotation quotidienne, 30 fichiers conservés par défaut, pilotée par `LOG_RETENTION_DAYS`
- [x] `LOG_DIR` vide désactive proprement la journalisation fichier
- [x] Un dossier de logs non créable ne bloque pas le démarrage (warning + stdout seul)
- [x] `GET /api/logs` renvoie les dernières lignes, respecte `lines` et `level`
- [x] La section Maintenance des réglages affiche, filtre et actualise le journal
- [x] Les tests n'écrivent aucun fichier de log hors du répertoire temporaire (`LOG_DIR=""` dans la fixture)
- [x] `ruff check` + `ruff format --check` + `pytest` au vert
- [x] `docs/installation.*.md` (emplacement, rétention) et `docs/developer.en.md` (variables) à jour

## Blocked by

None — can start immediately
