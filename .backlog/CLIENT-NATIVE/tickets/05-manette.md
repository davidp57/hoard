# BL-110 — Manette : navigation et couches de boutons

Status: ⬜ ready
Type: feat
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 03, 04
Files: `client/lib/`

## What to build

Le pilotage complet à la manette, sur le modèle des quatre couches de
l'interface web (base / L1 / R1 / L1+R1).

**Leçon de BL-104, et elle change l'approche :** le spike écoutait les touches
fléchées en supposant que Steam Input mappe la croix dessus. C'est vrai avec
certains profils seulement, et le profil appliqué par défaut à une application
non-Steam ne le fait pas — il a fallu changer le modèle de disposition à la
main pour avoir la croix, le pavé tactile donnant la souris d'emblée.

Dépendre d'un réglage que l'utilisateur doit trouver lui-même est fragile. Le
client doit **lire la manette directement** — `/dev/input` ou SDL — plutôt que
d'attendre un mapping vers le clavier.

## Acceptance criteria

- [ ] Toute l'interface atteignable à la manette sans réglage Steam préalable
- [ ] Les quatre couches de l'interface web reproduites
- [ ] Le clavier et le tactile restent des chemins valides
