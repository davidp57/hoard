# BL-107 — Client d'API et modèle de données

Status: ⬜ ready
Type: feat
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 01
Files: `client/lib/`

## What to build

La couche qui parle au serveur, extraite proprement du spike. Routes utiles :
`/api/files`, `/api/progress` (GET et POST), `/api/file`, `/api/search`,
`/api/settings`, `/api/tags`, `/api/quick-folders`, `/api/home-roots`.

Acquis de BL-104, à ne pas redécouvrir :

- **L'authentification Basic est en place côté serveur.** Chaque requête porte
  l'en-tête ; un `401` doit être un message lisible, pas une exception brute.
- **mpv a son propre client HTTP** : les identifiants doivent lui être passés
  séparément, en en-tête (`httpHeaders`) et non dans l'URL, pour qu'ils ne
  finissent ni dans un journal ni à l'écran.
- Les chemins sont relatifs à `MEDIA_ROOT`, tels que `/api/files` les renvoie.
- La configuration vient de l'environnement avant les préférences enregistrées :
  une valeur erronée mémorisée ne doit jamais devenir irrattrapable.

## Acceptance criteria

- [ ] Toutes les routes utiles couvertes, avec et sans authentification
- [ ] Un `401` produit un message actionnable
- [ ] Vérification de compatibilité de version au démarrage
