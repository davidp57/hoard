# BL-112 — Gestion de fichiers : déplacer, supprimer, renommer, dossiers rapides

Status: ⬜ ready
Type: feat
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 03, 06
Files: `client/lib/`

## What to build

Les actions sur fichiers et dossiers : déplacer avec sélecteur de destination,
supprimer avec confirmation, renommer, créer un dossier, épingler en accès
rapide.

Le serveur fait déjà le travail difficile et il faut en respecter le contrat :
une destination occupée renvoie **409** avec `{code, name, overwritable}`, et
c'est au client d'offrir le choix « écraser ou annuler » (voir lot
MOVE-COLLISION). Un dossier n'est jamais écrasable.

Les déplacements passent par un job asynchrone : suivre `/api/jobs` plutôt que
supposer le succès, et signaler un job en échec.

## Acceptance criteria

- [ ] Les quatre actions, avec le curseur préservé après coup
- [ ] Le `409` ouvre un choix écraser / annuler, annuler par défaut
- [ ] Un job en échec est visible, pas silencieux
