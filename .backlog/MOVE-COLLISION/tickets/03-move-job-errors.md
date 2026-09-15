# BL-092 — Un job de déplacement en échec doit se signaler

Status: 🔄 in-progress
Type: fix
Files: `backend/main.py`, `tests/test_api.py`

## What to build

`_run_move` n'avait pas de garde : une exception dans le thread laissait le job sur
`running` pour toujours, et l'interface attendait un déplacement qui n'arriverait
jamais. C'est ce qui rendait le plantage d'origine invisible côté utilisateur.

- Corps de `_run_move` entouré d'un `try/except` qui trace l'erreur et pose
  `status: "error"` avec le message.
- **`_move_with_retry(source, final_dest)`** isole la reprise sur `PermissionError`
  (un lecteur garde un instant le fichier ouvert), ce qui rend le chemin d'erreur
  lisible et testable.

## Acceptance criteria

- [x] Un échec au déplacement rend un job `error` porteur du message
- [x] La base est restaurée par `rollback` et le fichier source reste en place
