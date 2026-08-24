# BL-078 — Le worker de téléchargement meurt sur toute exception inattendue

Status: ✅ done
Type: fix
Files: `backend/main.py`, `tests/test_api.py`

## Problème

`_download_worker_loop()` enveloppait le traitement d'un job dans un `try/finally`
**sans `except`**. Toute exception échappant à `_run_download()` remontait à travers
la boucle `while True` et **tuait le thread démon `dl-worker` définitivement**.

Conséquence : tous les téléchargements suivants restaient bloqués en `pending`
**pour toujours**, sans erreur nulle part — ni dans l'interface, ni dans les logs.
Seul un redémarrage du container recréait le worker. C'est une cause racine
plausible du symptôme rapporté (« je ne retrouve pas mes derniers téléchargements »).

Les fenêtres d'exception hors du `try` interne de `_run_download` :

- `import yt_dlp` (première ligne de la fonction) — installation cassée ou en cours
  de mise à jour ;
- `_jobs[job_id]` / `job["_params"]` — `KeyError` si l'entrée a disparu du store
  entre l'enfilement et le traitement (`DELETE /api/jobs/{id}`).

Reproduit en local : avec `yt-dlp` absent, le premier téléchargement tuait le
worker et le second restait `pending` indéfiniment.

## Correctif

`except Exception` autour du traitement dans `_download_worker_loop` :
`logger.exception(...)`, passage du job en `error` avec le type et le message de
l'exception, persistance dans l'historique, et **le worker reste vivant**.

## Acceptance criteria

- [x] Une exception inattendue ne tue plus le thread `dl-worker`
- [x] Le job fautif passe en `error` avec un message exploitable
- [x] L'exception est journalisée avec sa trace complète
- [x] Un second téléchargement lancé après un échec est bien traité
- [x] Test de non-régression : worker survivant + statut `error` + job suivant traité

## Blocked by

None
