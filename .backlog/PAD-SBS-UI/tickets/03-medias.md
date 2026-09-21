# BL-132 — Vidéo, images et PDF

Status: ⬜ ready
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

Les trois visionneuses ne se recopient pas de la même façon, et l'une d'elles ne
se recopie pas du tout.

**Une `<video>` clonée ne joue pas.** Le clone repart de zéro, sans source
chargée, sans position ; le dupliquer donnerait deux lectures désynchronisées du
même fichier, donc deux téléchargements et deux décodages sur une machine choisie
faible. Et le lecteur **sait déjà** se dessiner en côte à côte : c'est tout
l'objet de [FEAT-VR180](../FEAT-VR180/PRD.md), qui dessine les deux yeux dans un
canvas WebGL.

**Un `<canvas>` cloné est vide** : le contenu d'un canvas n'est pas dans le DOM.
Cela vaut pour le canvas VR et pour la visionneuse d'images, qui zoome et
déplace.

**Les images et les PDF**, eux, se recopient — mais doublent les requêtes réseau
si on n'y prend pas garde.

## What to build

- **La zone du lecteur est exclue du miroir** quand elle se dessine déjà en côte à
  côte. Deux mécanismes qui dupliquent la même chose la quadruplent.
- **En mode plat ou hors VR**, décider quoi montrer plutôt que de laisser un trou :
  une vidéo lue sur un écran coupé en deux est de toute façon inconfortable. La
  réponse est peut-être d'imposer le mode côte à côte du lecteur tant que le mode
  global est allumé — **à trancher avec David**, parce que ça décide de ce qu'on
  voit en ouvrant une vidéo ordinaire dans des lunettes.
- **Images et PDF** : recopier sans redemander le fichier au serveur. Une même
  URL est normalement servie par le cache du navigateur, mais **le vérifier**
  plutôt que le supposer — c'est un NAS basse consommation au bout.
- **La visionneuse d'images zoome et se déplace** : son état de zoom n'est pas
  dans le DOM. Même traitement que les états de BL-131.

## Acceptance criteria

- [ ] Une image est lisible dans les deux yeux, sans requête réseau doublée
- [ ] Un PDF est lisible dans les deux yeux
- [ ] Le zoom et le déplacement d'une image suivent dans le miroir
- [ ] Une vidéo n'est **jamais** décodée deux fois — vérifié, pas supposé
- [ ] Ouvrir une vidéo ordinaire avec le mode global allumé donne un résultat
      décidé et documenté, pas un trou
- [ ] Le mode global et le côte à côte du lecteur ne se superposent pas

## Ce qu'il ne faut pas rater

**Le nombre de requêtes est l'observable qui tranche** pour les images et les
vignettes : le relever dans l'inspecteur réseau avant et après, sur un dossier
qui en contient beaucoup. Un doublement passerait inaperçu à l'œil et se paierait
sur le NAS.

**Le lecteur audio** existe aussi (`#audio-player`) et n'a pas été cité dans le
cadrage. Il n'a presque rien à afficher, mais il ne doit pas casser : le vérifier
en passant.
