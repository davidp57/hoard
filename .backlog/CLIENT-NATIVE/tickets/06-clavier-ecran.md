# BL-111 — Clavier à l'écran piloté à la manette

Status: ⬜ ready
Type: feat
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 05
Files: `client/lib/`

## What to build

Un clavier à l'écran pour la recherche, le renommage, les tags et la création
de dossiers.

**Le cadrage a changé après BL-104.** Ce ticket était justifié par
l'impossibilité de saisir du texte en mode Gaming — or `Steam+X` **fonctionne**
dans une application native : le défaut ne touchait qu'Edge. Le clavier maison
n'est donc plus une nécessité mais un **confort** : taper à la croix
directionnelle sans lâcher la manette reste plus agréable que d'invoquer le
clavier système.

À reprioriser en conséquence, voire à écarter si le clavier Steam suffit à
l'usage.

## Acceptance criteria

- [ ] Saisie complète à la manette, sans recourir au clavier système
- [ ] Le clavier système reste utilisable pour qui le préfère
