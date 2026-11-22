# BL-147 — Se connecter à Stash

Status: ✅ done
Lot: [FEAT-STASH](../PRD.md)

## Quoi

Décisions 2, 3 et 8 du PRD : réglages, clé en écriture seule, client GraphQL côté serveur, proxy des médias.

## Critères d'acceptation

- [x] Réglages `stash_url`, `stash_api_key`, `stash_folder` (défaut `[[_keep`), `stash_path_prefix`, `stash_identify` dans Paramètres (avec `applyCfg`) ; fonction coupée tant que `stash_url` est vide.
- [x] `stash_api_key` jamais renvoyée par `/api/settings` : seulement un booléen « clé enregistrée » ; la vider explicitement est possible.
- [x] Bouton « Tester la connexion » : affiche la version de Stash, ou l'erreur exacte (injoignable, 401, réponse non GraphQL).
- [x] Client GraphQL dans le backend (en-tête `ApiKey`, délai court, erreur `WARNING stash:` avec URL et cause dans le journal).
- [x] Correspondance de chemins Hoard ↔ Stash par remplacement de préfixe, dans les deux sens, testée, y compris un nom de dossier qui commence par `[[`.
- [x] Proxy `GET /api/stash/scene/{id}/{kind}` sur la liste fermée du PRD ; accepte le jeton signé existant ; refuse le reste.
- [x] Tests pytest avec un faux Stash (réponses GraphQL et médias simulés) : connexion, 401, injoignable, clé jamais exposée, proxy.
- [x] Doc : guide utilisateur FR + EN (créer la clé dans Stash, régler les champs, n'indexer que le dossier de Stash dans Stash) ; doc développeur (client, routes, réglages) ; `ROADMAP.md`.
