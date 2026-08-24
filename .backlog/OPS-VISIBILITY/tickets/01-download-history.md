# BL-075 — Persistance des téléchargements et vue historique

Status: ✅ done
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`, `docs/user-guide.*.md`, `docs/developer.en.md`

## What to build

Rendre les téléchargements traçables au-delà du TTL en mémoire et du cycle de vie du
container.

### Backend

- Table SQLite créée dans `init_db()` :

  ```sql
  CREATE TABLE IF NOT EXISTS downloads (
      id          TEXT PRIMARY KEY,   -- job uuid
      url         TEXT NOT NULL,
      title       TEXT,               -- hint envoyé par la bookmarklet
      output_name TEXT,               -- nom de fichier final
      output_path TEXT,               -- chemin relatif à MEDIA_ROOT
      status      TEXT NOT NULL,      -- pending|resolving|running|done|error|cancelled|interrupted
      error       TEXT,
      created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      finished_at TIMESTAMP
  );
  CREATE INDEX IF NOT EXISTS idx_downloads_created ON downloads(created_at DESC);
  ```

- Helper `_persist_download_job(job)` appelé à chaque transition d'état du job
  (création, `resolving`, `running`, terminal) — upsert sur `id`. `_jobs` reste le
  store de travail ; la DB en est le miroir durable.
- Au démarrage (`init_db()` ou juste après) : passer en `interrupted` toute ligne
  dont le statut n'est pas terminal, avec `finished_at = CURRENT_TIMESTAMP`.
- Purge : supprimer les lignes dont `created_at` dépasse la rétention, au démarrage
  puis à chaque appel de `_purge_old_jobs()`.
- Nouveaux réglages (`_SETTINGS_KEYS` + défauts + `SettingsUpdate`) :
  - `download_history_days` — défaut `0` = **illimité** (l'historique est léger et
    sert justement à retrouver un ajout ancien) ; toute valeur > 0 borne la rétention.
- Nouveaux endpoints :
  - `GET /api/downloads?limit=100&offset=0&status=` — historique trié par
    `created_at` décroissant. `status` filtre optionnel.
  - `DELETE /api/downloads` — vide l'historique (les jobs vivants ne sont pas touchés).
  - `DELETE /api/downloads/{id}` — supprime une entrée.

### Frontend

- Le modal du badge 📥 se scinde en deux sections :
  - **En cours** — jobs vivants (comportement actuel inchangé, y compris cancel et
    dismiss).
  - **Historique** — lignes de `/api/downloads`, avec nom de fichier, statut coloré,
    date, et pour les échecs le message d'erreur (repliable). Chargée à l'ouverture
    du modal, pas en polling.
- Sur une entrée réussie : action « Aller au fichier » qui navigue vers le dossier
  contenant et met la ligne en évidence.
- Bouton « Vider l'historique » en pied de section, avec confirmation.
- L'historique est aussi accessible sans job en cours (le badge 📥 reste cliquable
  même à zéro job actif).

## Acceptance criteria

- [x] La table `downloads` est créée au démarrage et migrée sans casser une base existante
- [x] Chaque téléchargement lancé apparaît en DB, avec son statut final et son erreur éventuelle
- [x] Un job non terminal survivant à un redémarrage est requalifié `interrupted`
- [x] Par défaut aucune purge de l'historique ; une valeur > 0 dans `download_history_days` purge au-delà
- [x] `GET /api/downloads` renvoie l'historique paginé, trié du plus récent au plus ancien
- [x] Le modal 📥 affiche « En cours » + « Historique », et l'historique est consultable sans job actif
- [x] Une entrée en échec montre le message d'erreur ; une entrée réussie permet d'aller au fichier
- [x] Tests : persistance des transitions, requalification `interrupted`, purge, endpoints + pagination
- [x] `ruff check` + `ruff format --check` + `pytest` au vert
- [x] Docs utilisateur (FR + EN) et `docs/developer.en.md` à jour, `CHANGELOG.md` + `docs/changelog-user.fr.md`

## Blocked by

None — can start immediately
