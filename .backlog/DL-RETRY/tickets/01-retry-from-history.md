# BL-084 — Relancer un téléchargement depuis l'historique

Status: ✅ done
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`, `docs/user-guide.*.md`, `docs/developer.*.md`

## What to build

### Backend

- **Persister le `referer`** : colonne ajoutée à `downloads` avec migration
  (`PRAGMA table_info` + `ALTER TABLE`). Sans elle, relancer une URL de CDN direct
  échouerait sur les contrôles d'origine — le cas d'usage principal.
- **Factoriser `_queue_download(url, *, title, referer, cookies)`** depuis
  `start_download`, pour que la relance emprunte la même validation, la même
  destination et la même file séquentielle.
- **`POST /api/downloads/{id}/retry`** : lit `url`, `title`, `referer` depuis la
  ligne d'historique, journalise `download retried: from=… url=… ip=…`, renvoie
  `{job_id}`. 404 si l'entrée n'existe pas. L'URL est **revalidée** — une entrée
  d'historique ne contourne pas la protection SSRF.

### Frontend

- Bouton **↻** sur chaque entrée de l'historique, avec infobulle et `aria-label`.
- Sur une entrée **réussie** : confirmation annonçant qu'un second fichier sera
  créé (le nom sera suffixé ` (2)` par le mécanisme anti-collision de BL-079).
- Après la relance : toast, redémarrage du poller de file, rafraîchissement de
  l'historique.
- **Zone de clic tactile** : les boutons-icônes de la ligne (`↻` et `✕`) faisaient
  8×12 et 11×13 px. Portés à 24×26 via padding + marge négative — la marge évite
  d'augmenter la hauteur des lignes. Le projet cible un laptop tactile et un iPad.

## Acceptance criteria

- [x] Le bouton relance la même URL et crée une nouvelle entrée d'historique
- [x] Le `referer` d'origine est conservé et retransmis
- [x] Le titre d'origine est conservé
- [x] Une entrée réussie demande confirmation ; un refus ne lance rien
- [x] Une entrée inconnue renvoie 404
- [x] L'URL est revalidée (une adresse locale est rejetée en 400)
- [x] Les boutons-icônes atteignent une cible d'au moins 24 px sans grossir les lignes
- [x] Vérifié en conditions réelles : une entrée en échec relancée aboutit et écrit le fichier
- [x] `ruff check` + `ruff format --check` + `pytest` au vert

## Blocked by

None
