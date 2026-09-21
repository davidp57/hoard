# BL-124 — Jeton dédié pour la bookmarklet

Status: ✅ done
Type: fix
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`,
`docs/user-guide.*.md`, `docs/installation.*.md`

## Problem

Depuis l'activation de l'authentification en production, **la bookmarklet de
téléchargement ne fonctionne plus**. Elle poste vers Hoard depuis la page tierce
où l'on se trouve, donc en *cross-origin* : le navigateur n'attache pas les
identifiants Basic, et le CORS en `allow_origins=["*"]`
(`backend/main.py:164`) interdit de le lui demander.

### Reproduction (faite — le diagnostic était incomplet)

Reproduit sur une page servie depuis une origine distincte, contre une instance
avec `HOARD_AUTH_USER`/`HOARD_AUTH_PASS` définis. Le diagnostic ci-dessus est
**vrai mais n'est pas ce qui frappe en premier**, et il manquait deux choses :

1. **La requête préflight `OPTIONS` est elle-même refusée.** Le POST porte
   `Content-Type: application/json`, donc le navigateur demande d'abord la
   permission ; or `require_basic_auth` s'exécute **à l'extérieur** de
   `CORSMiddleware` (`add_middleware` empile le dernier ajouté le plus à
   l'extérieur) et lui répond un 401 nu, sans en-tête CORS. Relevé :
   `Response to preflight request doesn't pass access control check: No
   'Access-Control-Allow-Origin' header`. **Le vrai POST n'est jamais émis** —
   aucune réponse 401 n'atteint donc la bookmarklet, contrairement à ce que le
   ticket supposait.
2. **Conséquence sur le symptôme** : le `fetch` part en rejet, la branche
   `.catch` s'exécute, et elle annonce « Site incompatible (CSP) ». La panne se
   présentait donc comme une incompatibilité de site, pas comme un défaut
   d'authentification.
3. **Le second volet tient**, vérifié séparément sur une route exemptée d'auth :
   avec `allow_origins=["*"]`, un `credentials:"include"` est refusé
   explicitement (`must not be the wildcard '*' when the request's credentials
   mode is 'include'`). Ajouter les identifiants n'aurait rien réparé.

**Ce que la reproduction a ajouté au périmètre.** La bookmarklet fait **deux**
appels : le POST de démarrage, puis un sondage de `/api/jobs` toutes les 2 s.
Réparer le premier seul aurait laissé le second en 401, avalé par un `catch`
vide — dialogue figé sur « Analyse de l'URL… » indéfiniment, soit exactement
l'échec silencieux que ce ticket veut supprimer. Arbitré avec David : une route
d'état dédiée en POST (`/api/download/status`), qui ne répond que sur la tâche
demandée.

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

- [x] La bookmarklet fonctionne avec l'authentification activée
- [x] Un jeton faux ou absent rend `401` sur `/api/download` (test)
- [x] Le jeton **ne donne accès à rien d'autre** : `/api/files`, `/api/files/move`
      et `DELETE /api/files` le refusent (test)
- [x] Le jeton n'apparaît dans aucune URL, ni côté client ni dans les journaux
- [x] Régénérer le jeton invalide l'ancien (test)
- [x] La comparaison se fait en temps constant
- [x] Un échec d'authentification de la bookmarklet est **visible** pour
      l'utilisateur, pas silencieux

## À vérifier d'abord

Reproduire la panne avant de la corriger : lancer la bookmarklet sur une instance
avec l'authentification active et relever le code de retour. Le diagnostic ci-dessus
vient de la lecture du code ; s'il est faux, ce ticket change de forme.
