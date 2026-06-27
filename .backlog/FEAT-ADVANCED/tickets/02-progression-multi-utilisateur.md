# BL-015 — Progression de lecture multi-utilisateur

Status: ⬜ ready
Type: feat
Files: `backend/main.py`, `tests/test_api.py`, `docs/developer.en.md`

## What to build

Séparer la progression de lecture par utilisateur. Aujourd'hui la table `progress`
a une seule ligne par `path` ; plusieurs personnes sur la même instance écrasent
mutuellement leur avancement. Dériver une clé utilisateur de l'auth HTTP Basic
(BL-011, livrée) et étendre les lignes `progress` par utilisateur, sans rompre le
mode mono-utilisateur (auth désactivée → comportement actuel inchangé).

## Acceptance criteria

- [ ] La progression est isolée par utilisateur quand l'auth Basic est active
- [ ] Sans auth (mono-utilisateur), aucun changement de comportement ni de schéma visible
- [ ] Migration `init_db()` idempotente (pas d'outil de migration externe)
- [ ] Tests : isolation par utilisateur + non-régression mono-utilisateur
- [ ] `ruff check` + `ruff format --check` + `pytest` au vert

## Blocked by

None — BL-011 (auth HTTP Basic) est livré (lot `SECURITY-QUALITY-UX`)
