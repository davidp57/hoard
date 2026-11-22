# BL-147 — Se connecter à Stash

Status: ⬜ ready
Lot: [FEAT-STASH](../PRD.md)

## Quoi

Décisions 2, 3 et 8 du PRD : réglages, clé en écriture seule, client GraphQL côté serveur, proxy des médias.

## Critères d'acceptation

- [ ] Réglages `stash_url`, `stash_api_key`, `stash_folder` (défaut `_stash`), `stash_path_prefix` dans Paramètres (avec `applyCfg`) ; fonction coupée tant que `stash_url` est vide.
- [ ] `stash_api_key` jamais renvoyée par `/api/settings` : seulement un booléen « clé enregistrée » ; la vider explicitement est possible.
- [ ] Bouton « Tester la connexion » : affiche la version de Stash, ou l'erreur exacte (injoignable, 401, réponse non GraphQL).
- [ ] Client GraphQL dans le backend (en-tête `ApiKey`, délai court, erreur `WARNING stash:` avec URL et cause dans le journal).
- [ ] Correspondance de chemins Hoard ↔ Stash par remplacement de préfixe, dans les deux sens, testée.
- [ ] Proxy `GET /api/stash/scene/{id}/{kind}` sur la liste fermée du PRD ; accepte le jeton signé existant ; refuse le reste.
- [ ] Tests pytest avec un faux Stash (réponses GraphQL et médias simulés) : connexion, 401, injoignable, clé jamais exposée, proxy.
- [ ] Doc : guide utilisateur FR + EN (créer la clé dans Stash, régler les quatre champs, créer le dossier et l'ajouter à Stash) ; doc développeur (client, routes, réglages) ; `ROADMAP.md`.
