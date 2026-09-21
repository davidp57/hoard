# BL-108 — Navigation : dossiers, états de lecture, tri, recherche

Status: ⬜ ready
Type: feat
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 02
Files: `client/lib/`

## What to build

Le navigateur de fichiers : liste d'un dossier, fil d'Ariane, états non-vu /
en-cours / vu avec pourcentage, les cinq critères de tri de l'interface web,
recherche, filtrage par tag, racines multiples.

À surveiller : les listes peuvent compter des milliers d'entrées (≈ 1 800
fichiers en 1080p sur l'instance de référence). Virtualisation obligatoire, et
les miniatures se chargent à la demande.

## Acceptance criteria

- [ ] Parité fonctionnelle avec la liste de l'interface web
- [ ] Défilement fluide sur un dossier de plusieurs milliers d'entrées
- [ ] Les états de lecture sont ceux du serveur, partagés avec le web
