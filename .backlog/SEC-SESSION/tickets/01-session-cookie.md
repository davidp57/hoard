# BL-123 — Écran de connexion et session par cookie

Status: ✅ done
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`,
`docs/installation.*.md`, `docs/user-guide.*.md`, `docs/developer.en.md`

## Problem

L'authentification Basic est activée en production. Elle oblige à ressaisir les
identifiants à chaque nouvelle fenêtre, par la fenêtre native du navigateur — qui
se pilote mal à la manette sur le Deck et le Frame, et ne ressemble à rien du reste
de l'interface.

## What to build

### Backend

- `POST /api/login` : corps `{user, password}`, comparaison en **temps constant**
  sur les deux champs (comme `_check_basic_auth` le fait déjà). En cas de succès,
  pose le cookie ; en cas d'échec, `401` sans détail sur ce qui a échoué.
- **Cookie `hoard_session`** : `HttpOnly`, `SameSite=Lax`, `Path=/`,
  `Max-Age` 30 jours, `Secure` piloté par un réglage d'environnement
  (`HOARD_COOKIE_SECURE`, défaut `1`). Le backend est derrière le reverse proxy
  Synology : il reçoit du HTTP en interne et **ne peut pas** deviner que le client
  est en HTTPS, d'où le réglage plutôt qu'une détection.
- **Contenu signé, pas chiffré** : `{utilisateur, expiration}` + HMAC-SHA256.
  Vérifier la signature **avant** de lire le contenu, et rejeter une expiration
  dépassée.
- **Clé de signature** : `HOARD_SECRET_KEY` si elle existe, sinon une clé générée
  au premier démarrage (`secrets.token_urlsafe`) et rangée dans `settings`. La
  changer invalide toutes les sessions — c'est le mécanisme de révocation.
- **Renouvellement glissant** : si le cookie est valide et qu'il reste moins de la
  moitié de sa durée, le reposer. Sinon « 30 jours » veut dire « 30 jours après la
  première connexion », ce qui ramène la ressaisie qu'on cherche à supprimer.
- **Middleware** : `/healthz` exempté, puis cookie valide, puis Basic valide, sinon
  `401`. L'ordre compte peu, mais le cookie d'abord évite de décoder du base64 à
  chaque requête.
- **`WWW-Authenticate` uniquement pour les requêtes non-HTML** (pas d'`Accept:
  text/html`). Tant qu'il part vers un navigateur, celui-ci ouvre sa propre fenêtre
  et l'écran de connexion ne s'affiche jamais. Il reste nécessaire à `curl -u`, qui
  n'envoie ses identifiants qu'après avoir reçu le défi.
- `POST /api/logout` : efface le cookie. Corollaire technique d'un cookie, pas un
  objectif du lot.

### Frontend

- Un écran de connexion sur le modèle de `#pin-screen` : même style, pilotable au
  clavier et **à la manette** (c'est le besoin d'origine sur le Deck).
- Affiché quand une requête d'API rend `401`, et au démarrage si la session manque.
- Après succès, rejouer le chargement normal sans recharger la page.

## Acceptance criteria

- [x] Se connecter par l'écran pose le cookie, et la navigation suivante ne
      redemande rien
- [x] Les identifiants faux rendent `401` et **ne posent pas** de cookie
- [x] Un cookie dont la signature est falsifiée est rejeté (test)
- [x] Un cookie expiré est rejeté (test)
- [x] Le cookie porte `HttpOnly`, `SameSite=Lax`, et `Secure` selon le réglage
- [x] Le renouvellement glissant repose le cookie passé la moitié de sa durée
- [x] **Basic continue de fonctionner** : `curl -u` reçoit son défi et passe (test)
- [x] Un navigateur ne reçoit plus `WWW-Authenticate`, donc plus de fenêtre native
- [x] `/healthz` reste joignable sans rien
- [x] L'écran de connexion se pilote entièrement à la manette
- [x] Changer `HOARD_SECRET_KEY` invalide les sessions en cours (test)

## Ce qu'il ne faut pas rater

Le cookie **introduit le risque CSRF**, que Basic n'avait pas : un site tiers ne
pouvait rien déclencher, un cookie le permettrait. L'API expose
`DELETE /api/files` et `POST /api/files/move`. `SameSite=Lax` ferme cette porte
sur les navigateurs actuels — c'est la raison d'être de l'attribut, et il n'est pas
optionnel ici.

## Ce que la réalisation a ajouté

**La page de Hoard devait être servie sans authentification** — préalable non vu
au cadrage, et qui bloquait tout le ticket. La page est elle-même derrière le
middleware : en retirant `WWW-Authenticate`, un navigateur non connecté recevait
un **401 vide**, sans fenêtre native ni écran de connexion — aucun moyen d'entrer.
Arbitré avec David : quatre chemins exemptés (`/`, `/index.html`,
`/service-worker.js`, `/manifest.webmanifest`), toutes les routes `/api/*` restant
gardées. Ce que ça montre à un inconnu est la structure de l'application, déjà
publique puisque le dépôt l'est.

**Un défaut trouvé à la vérification manette et corrigé.** La règle
`#login-form input:focus { outline: none }` aurait effacé le curseur de la manette
exactement quand celle-ci se pose sur un champ — une règle d'ID l'emporte sur
`.gp-modal .gp-cursor`. Corrigé en `:focus:not(.gp-cursor)`. La première mesure,
prise dans un onglet qui n'avait pas le focus, ne prouvait rien : `:focus` ne s'y
appliquait pas. Re-mesuré document au premier plan, avant/après.

**Non vérifiable avec l'outillage :** la soumission par la touche Entrée. Les
frappes simulées ne déclenchent pas la soumission implicite native du navigateur.
Le câblage a été vérifié autrement (`form.requestSubmit()` déclenche bien
`submitLogin`, la session s'établit), et le formulaire est un `<form>` standard
avec un `<button type="submit">` ; aucun gestionnaire n'appelle `preventDefault`
sur Entrée (mesuré : `defaultPrevented=false` après tous les gestionnaires de
l'application).
