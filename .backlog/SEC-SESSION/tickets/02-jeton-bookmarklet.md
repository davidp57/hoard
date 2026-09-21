# BL-124 — Jeton dédié pour la bookmarklet

Status: ⬜ ready
Type: fix
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`,
`docs/user-guide.*.md`, `docs/installation.*.md`

## Problem

Depuis l'activation de l'authentification en production, **la bookmarklet de
téléchargement ne fonctionne plus**. Elle poste vers Hoard depuis la page tierce
où l'on se trouve, donc en *cross-origin* : le navigateur n'attache pas les
identifiants Basic, et le CORS en `allow_origins=["*"]`
(`backend/main.py:164`) interdit de le lui demander.

À confirmer d'un essai réel — le diagnostic est tiré de la lecture du code, pas
d'une reproduction.

**Le cookie de BL-123 ne réparera pas ça**, et c'est voulu : un cookie correct est
`SameSite=Lax`, ce qui l'empêche par construction de partir depuis un site tiers.
C'est exactement la protection qu'on veut garder. Il faut donc un second
mécanisme, volontairement étroit.

## What to build

- **Un jeton de téléchargement** généré par `secrets.token_urlsafe(32)`, rangé dans
  `settings`, créé à la demande. Affiché dans les réglages à côté de la
  bookmarklet, avec un bouton pour le régénérer (ce qui invalide l'ancien).
- **Le jeton voyage dans le corps de la requête**, jamais dans l'URL ni dans la
  query : un jeton d'authentification dans une URL finit dans les journaux du
  reverse proxy et dans l'historique. Le POST de la bookmarklet est déjà du JSON,
  donc il suffit d'un champ — et rien ne change au CORS.
- **Le jeton n'ouvre que `POST /api/download`.** Il circule dans un marque-page,
  sur n'importe quel site : il ne doit ni lister, ni déplacer, ni supprimer.
  Comparaison en temps constant, comme le reste.
- **La bookmarklet est regénérée** avec le jeton dedans, depuis la page des
  réglages ; régénérer le jeton doit donc aussi proposer de réinstaller le
  marque-page.
- Si le jeton est absent ou faux, `401` — et le message d'erreur de la bookmarklet
  doit le dire clairement, sinon l'échec reste aussi silencieux qu'aujourd'hui.

## Acceptance criteria

- [ ] La bookmarklet fonctionne avec l'authentification activée
- [ ] Un jeton faux ou absent rend `401` sur `/api/download` (test)
- [ ] Le jeton **ne donne accès à rien d'autre** : `/api/files`, `/api/files/move`
      et `DELETE /api/files` le refusent (test)
- [ ] Le jeton n'apparaît dans aucune URL, ni côté client ni dans les journaux
- [ ] Régénérer le jeton invalide l'ancien (test)
- [ ] La comparaison se fait en temps constant
- [ ] Un échec d'authentification de la bookmarklet est **visible** pour
      l'utilisateur, pas silencieux

## À vérifier d'abord

Reproduire la panne avant de la corriger : lancer la bookmarklet sur une instance
avec l'authentification active et relever le code de retour. Le diagnostic ci-dessus
vient de la lecture du code ; s'il est faux, ce ticket change de forme.
