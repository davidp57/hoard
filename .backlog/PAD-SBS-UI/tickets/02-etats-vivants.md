# BL-131 — Les états que le HTML ne transporte pas

Status: ✅ done
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

Recopier du HTML ne recopie pas tout. Plusieurs états **ne sont pas dans le
balisage** et disparaîtront donc du miroir, chacun d'une façon qui rend
l'interface inutilisable dans l'œil qui lit la copie :

| État | Ce qu'on voit dans le miroir sans le traiter |
|---|---|
| Position de défilement | la copie reste en haut pendant qu'on descend |
| Champ en cours de saisie | le texte tapé n'apparaît pas — `value` n'est pas un attribut |
| Élément sélectionné (`<select>`) | la copie montre la première option |
| Curseur manette | il se déplace dans l'original seul |
| État ouvert/fermé d'un dialogue natif | un `<dialog>` cloné n'est pas ouvert |
| Case cochée | `checked` n'est pas non plus un attribut |

Le curseur manette est le plus grave : **c'est le moyen de naviguer**, et sur la
machine visée il n'y a pas de souris. Un curseur invisible dans l'œil qu'on
regarde revient à naviguer à l'aveugle.

## What to build

- **Reporter chacun de ces états** sur le miroir après chaque recopie. Le
  défilement se synchronise déjà pour la carte des boutons (BL-127) : étendre le
  principe, élément par élément, plutôt que d'espérer que la recopie suffise.
- **Traiter la saisie en particulier.** `input.value` ne se recopie pas ; il faut
  le poser explicitement. Même chose pour `checked`, `selectedIndex` et l'état
  ouvert d'un `<dialog>`.
- **Vérifier le curseur manette dans les deux copies**, pour chaque écran qui en
  a un : le navigateur de fichiers, le menu Select, les dialogues, la page de
  réglages.

## Acceptance criteria

- [x] Le défilement de la liste suit dans le miroir
- [x] Le texte tapé dans un champ apparaît dans le miroir
- [x] Une case cochée, une option choisie apparaissent dans le miroir
- [x] Le curseur manette est visible **dans les deux copies**, sur tous les écrans
      qui en ont un
- [x] Un dialogue ouvert apparaît ouvert dans le miroir
- [x] Mesuré écran par écran, pas jugé sur un seul

## Ce qu'il ne faut pas rater

**Le code PIN ne doit pas être recopié en clair.** L'écran de code PIN est le
premier écran du lot ; son champ est un `<input type="password">`, mais reporter
`value` sur le miroir écrirait le code dans le DOM. Reporter la **longueur**, pas
le contenu — le miroir doit montrer le bon nombre de points, rien de plus.

**Le curseur manette est une classe** (`.gp-cursor`) et se déplace d'un élément à
l'autre : si la recopie est regroupée sur une image, le curseur peut accuser un
retard d'une image. À mesurer — un retard visible à l'œil serait pire qu'un
curseur absent, parce qu'il ferait douter de ce qu'on regarde.
