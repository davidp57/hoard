# BL-081 — Le test de redémarrage peut tuer le lanceur de tests

Status: ✅ done
Type: fix
Files: `tests/test_api.py`, `tests/conftest.py`

## Problème

Dette introduite par BL-077, signalée pendant la release v2.5.0 et restée ouverte.

`TestRestart` remplace `_terminate_process` par un double, puis attend l'événement
avec un timeout de 5 s. `POST /api/restart` lance un thread qui dort 0,5 s avant
d'appeler `_terminate_process`. Si l'attente expirait sur un runner chargé,
`monkeypatch` restaurerait la vraie fonction **avant** le réveil du thread, et
celui-ci appellerait le vrai `os.kill(os.getpid(), SIGTERM)` : le processus pytest
est tué en pleine session.

Course toujours gagnée en local, mais rien ne la garantit sur un runner CI — et le
symptôme serait un job qui meurt sans explication.

## Correctif

- Fixture `autouse` de session dans `conftest.py` : `_terminate_process` est
  neutralisé pour **toute** la suite. Aucun test, présent ou futur, ne peut plus
  atteindre le vrai `os.kill`.
- Les tests d'endpoint patchent `_delayed_terminate` (pas de thread dormant, pas de
  course).
- L'indirection `_delayed_terminate` → `_terminate_process` est testée séparément
  en **synchrone**, avec un délai nul.

## Acceptance criteria

- [x] Aucun chemin de test ne peut appeler le vrai `_terminate_process`
- [x] Les tests de `/api/restart` ne dépendent plus d'une attente temporisée
- [x] L'appel de `_delayed_terminate` à `_terminate_process` reste couvert
- [x] `pytest` au vert, sans ralentissement notable

## Blocked by

None — can start immediately
