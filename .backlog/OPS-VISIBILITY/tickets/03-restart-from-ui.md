# BL-077 — Redémarrer Hoard depuis l'interface

Status: ✅ done
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`, `docs/user-guide.*.md`, `docs/installation.*.md`, `docs/developer.en.md`

## What to build

Permettre de relancer l'application depuis les réglages, sans passer par Portainer
ni SSH sur le NAS.

### Backend

- `POST /api/restart` :
  - refuse (409) si un job de téléchargement est actif, sauf `force=true` dans le
    corps de requête — un redémarrage interrompt le téléchargement en cours ;
  - journalise `restart requested: ip=…` ;
  - répond `200 {"ok": true, "supervised": <bool>}` **avant** de terminer, pour que
    le client reçoive la réponse ;
  - termine le process après un court délai dans un thread démon, via une fonction
    dédiée `_terminate_process()` (point d'injection pour les tests) qui envoie
    `SIGTERM` au PID courant.
- `supervised` : vrai quand `RESTART_SUPERVISED` vaut 1 (défaut : vrai si le process
  tourne dans un container, détecté via l'existence de `/.dockerenv`). Sert
  uniquement à adapter le message de l'interface — le backend ne relance jamais
  lui-même.
- Le relancement est la responsabilité du superviseur : `restart: unless-stopped`
  est déjà présent dans `docker-compose.yml`. **Hors container, le bouton arrête
  l'application** — à écrire noir sur blanc dans la confirmation et la doc.

### Frontend

- Réglages → section **Maintenance** → bouton « Redémarrer Hoard ».
- Confirmation explicite, dont le texte change selon `supervised` :
  - supervisé : « Hoard va redémarrer, la page se rechargera automatiquement. »
  - non supervisé : « Hoard va s'arrêter et ne redémarrera pas tout seul. »
- Si un téléchargement est en cours, la confirmation le signale et demande une
  validation renforcée avant d'envoyer `force=true`.
- Après l'appel : écran d'attente qui interroge `/api/settings` toutes les 2 s
  (jusqu'à 60 s) et recharge la page dès que le backend répond. Message d'échec
  explicite au-delà du délai.

## Acceptance criteria

- [x] `POST /api/restart` répond avant de terminer le process
- [x] Un job de téléchargement actif provoque un 409, contournable par `force=true`
- [x] La demande de redémarrage est journalisée avec l'IP appelante
- [x] Le bouton est présent dans la section Maintenance des réglages, avec confirmation
- [x] Le texte de confirmation distingue le cas supervisé du cas non supervisé
- [x] L'interface attend le retour du backend et recharge automatiquement, avec un échec explicite après 60 s
- [x] Le test de l'endpoint ne tue pas le process de test (`_terminate_process` remplacé par un double)
- [x] `ruff check` + `ruff format --check` + `pytest` au vert
- [x] Docs utilisateur (FR + EN) et installation à jour, `CHANGELOG.md` + `docs/changelog-user.fr.md`

## Blocked by

BL-076 — crée la section « Maintenance » des réglages où le bouton se place.
(Dépendance de présentation uniquement : les deux tickets sont réalisables en
parallèle si la section est créée par le premier des deux à passer.)
