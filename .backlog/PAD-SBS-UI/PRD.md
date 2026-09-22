# Lot PAD-SBS-UI — Toute l'interface en côte à côte, sur bascule

Status: ✅ done
Branch: `feature/pad-sbs-ui` (à créer)

## Problem Statement

Des lunettes XR en mode 3D coupent l'image en deux **en permanence**, pas seulement
pendant une lecture. Toute l'interface de Hoard — l'écran de code PIN, le
navigateur de fichiers, les visionneuses d'images et de PDF, les dialogues — est
donc dessinée une fois, à cheval sur la coupure : chaque œil n'en voit qu'une
moitié.

En sortir n'est pas une porte de sortie. David, le 2026-09-21 : « je peux en
sortir mais ça coupe l'image 10 secondes et parfois ça pète les réglages ».

Le lot [PAD-VR](../PAD-VR/PRD.md) a traité **trois éléments** — le menu Select, la
carte des boutons et les messages du lecteur — parce que ce sont ceux qui servent
à piloter pendant une lecture VR. Le reste est resté, et c'est le reste qu'on
utilise le plus longtemps : on navigue bien plus qu'on ne règle.

Ce lot ne sert pas que les Viture Beast. Le **Steam Frame** posera exactement la
même contrainte.

## Solution

Un **mode d'affichage côte à côte, activable et désactivable à la demande**, qui
duplique l'interface entière par œil. Cadrage arrêté avec David le 2026-09-21 :
c'est une **bascule**, et elle couvre **toute l'application** — code PIN,
navigateur, images, PDF, vidéo et dialogues.

Trois choses le distinguent de ce que PAD-VR a fait :

1. **Il est global et permanent**, pas lié à la lecture d'un fichier. Le drapeau
   de PAD-VR (`body.vr-sbs-active`) n'est posé que le temps d'une lecture en mode
   côte à côte.
2. **Il doit couvrir ce qu'on n'a pas prévu.** Recopier trois boîtes à chaque
   rendu était tenable parce qu'on connaissait les trois points de rendu. À
   l'échelle de l'application, une liste se filtre, se trie, se rafraîchit toute
   seule pendant un téléchargement : un mécanisme qui demande de déclarer chaque
   point de rendu finira par en oublier un, et un miroir figé sur un état périmé
   est pire que pas de miroir.
3. **Il porte des états que le HTML ne transporte pas** : position de défilement,
   champ en cours de saisie, élément sélectionné, curseur manette, lecture vidéo
   en cours.

## Le réglage est propre à l'appareil, pas au compte

Contrairement à tout le reste, **il ne doit pas suivre d'une machine à l'autre** :
le Deck avec les lunettes en a besoin, le laptop et l'iPad non. C'est exactement
le cas que `localStorage` couvre dans ce dépôt — la règle « `localStorage` sert au
volume et à rien d'autre » vaut parce que le volume est le seul réglage
device-local qui existait. Celui-ci en est un second, et le ranger côté serveur
dupliquerait le mode sur des écrans qui n'en veulent pas.

**À vérifier au moment de le faire** : l'écran de code PIN s'affiche avant tout le
reste et avant que les réglages soient chargés. Le mode doit donc être lisible
sans appel réseau, ce qui va dans le même sens.

## User Stories

1. En tant qu'utilisateur sur Deck + lunettes XR, je veux lire l'interface entière
   sans sortir les lunettes du mode 3D, parce qu'en sortir coûte dix secondes
   d'écran noir et casse parfois mes réglages.
2. En tant qu'utilisateur, je veux allumer et éteindre ce mode d'un geste, depuis
   la manette comme au clavier — y compris quand l'écran est illisible parce que
   je viens de l'allumer par erreur sur un écran normal.
3. En tant qu'utilisateur, je ne veux pas que ce mode suive sur mon iPad.

## Découpage

| # | Ticket | Dépend de | Statut |
|---|---|---|---|
| 01 | [BL-130](tickets/01-miroir-global.md) — Le miroir global et sa bascule | — | ✅ |
| 02 | [BL-131](tickets/02-etats-vivants.md) — Les états que le HTML ne transporte pas | BL-130 | ✅ |
| 03 | [BL-132](tickets/03-medias.md) — Vidéo, images et PDF | BL-130 | ✅ |

## Décisions prises en cours de lot

- **La vidéo plate (question ouverte de BL-132), tranchée par David le 2026-09-22.**
  Option retenue : le lecteur ne double rien, c'est le miroir qui montre la même
  image entière dans chaque œil, peinte depuis le même élément `<video>`. Un
  téléchargement, un décodage, une recopie GPU par image. Le montage envisagé au
  cadrage — un rendu plein écran coupé en deux — n'avait pas lieu d'être : les
  deux yeux voient la **même** image, pas deux moitiés.
- **Préséance des deux mécanismes** : le mode global l'emporte. Tant qu'il est
  allumé, `setVrMode('sbs')` est ramené à `flat`, `sbs` sort du cycle de la touche
  **V**, et les copies par fenêtre de BL-127 sont éteintes.
- **Raccourcis** : manette **L1+R1+Select** (le chemin qui compte — David, le
  2026-09-22 : « dans tous les cas ça ne sera pas au clavier, Deck avec Beasts ou
  Steam Frame »), clavier **Y** / **Alt+Y**, menu Select, et Paramètres.
- **Deux surprises par rapport au cadrage.** Le ticket 01 ne prévoyait que le
  piège des identifiants dupliqués ; deux des trois requêtes fatales portaient en
  fait sur des **classes**, d'où le `shadow root` plutôt qu'un retrait des
  identifiants. Et le ticket 03 annonçait que le PDF « se recopie » : il se dessine
  dans un `<canvas>`, donc il est repeint comme la vidéo.

## Hors périmètre

- **La lecture immersive OpenXR** — écartée par [ADR 0003](../../docs/adr/0003-client-natif.md).
  Ce lot affiche une interface plate deux fois ; il ne fait pas de stéréoscopie et
  ne calcule aucune parallaxe. Les deux yeux voient **la même chose**, ce qui est
  précisément ce qui rend l'interface lisible et confortable.
- **Le client natif Flutter** ([CLIENT-NATIVE](../CLIENT-NATIVE/PRD.md)) : il aura
  le même besoin, mais il le résoudra chez lui.
