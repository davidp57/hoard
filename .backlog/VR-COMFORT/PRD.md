# Lot VR-COMFORT — Que la profondeur soit juste, et réglable en regardant

Status: ✅ done
Branch: plusieurs (correctifs de recette, un par sujet)

## Problem Statement

La recette de [PAD-SBS-UI](../PAD-SBS-UI/PRD.md) sur Deck + Viture Beast a
révélé un défaut qui était là depuis [FEAT-VR180](../FEAT-VR180/PRD.md) et que
personne n'avait pu voir : **le relief était faux**, et il l'était pour une
raison géométrique, pas esthétique.

David, le 2026-09-22 : « le relief est exagéré… en particulier quand quelque
chose se rapproche de la caméra, la sensation de profondeur et la taille
apparente des objets sont beaucoup trop prononcées ».

La cause : le lecteur affichait **90°** de la source sur toute la largeur de ce
que les lunettes présentent à un œil — or elles n'en présentent qu'environ
**45°**. Chaque objet était donc vu sous un angle deux fois et demie plus petit
que celui sous lequel la caméra l'avait pris. Le cerveau juge la distance à
l'écart entre les deux images ; cet écart était réduit d'autant, et le monde
paraissait géant et lointain. Quand un objet s'approchait, il enflait pendant
que les yeux disaient « c'est encore loin » — le conflit décrit.

**La condition juste est que l'angle sur la rétine égale l'angle vu par la
caméra**, c'est-à-dire que le réglage vaille le champ réel de l'affichage.

## Solution

Trois choses, dont deux faites.

1. Le défaut passe à 45°, et le réglage cesse de se présenter comme un zoom :
   ce qu'il faut y mettre, c'est le champ de l'écran qu'on utilise.
2. La convergence devient réglable assez vite et assez loin pour caler les yeux
   à ce champ — à 45° l'image est 2,4× plus agrandie qu'à 90°, et tout
   désalignement entre les deux yeux l'est avec elle.
3. Reste le compromis qu'on ne peut pas supprimer : **plus la profondeur est
   juste, moins on voit de la scène**. Les deux sont le même bouton.

## Le compromis, et pourquoi il est dur

Sur un écran plat qui occupe un angle fixe devant l'œil, « combien de scène je
vois » et « quelle profondeur je perçois » ne sont pas deux réglages : c'est le
même. Élargir le champ rapetisse tous les angles, donc l'écart entre les deux
images, donc la profondeur. La convergence ne rachète rien : elle **décale** la
scène, elle n'en change pas l'échelle.

La vraie solution de stéréographe — rapprocher les caméras — demanderait de
fabriquer un point de vue qui n'a pas été filmé, donc une carte de profondeur
par pixel en temps réel. Hors de portée du NAS comme du Deck.

Ce qui reste possible est de **ne pas comprimer partout pareil** : garder le
centre à l'échelle juste et comprimer les bords. C'est le ticket BL-135.

## User Stories

1. En tant qu'utilisateur sur Deck + lunettes XR, je veux que la profondeur
   d'une vidéo 180° soit juste sans avoir à deviner un réglage.
2. En tant qu'utilisateur, je veux caler mes yeux pendant la lecture, en
   regardant l'image se caler, pas en ouvrant un menu qui la recouvre.
3. En tant qu'utilisateur, je veux voir plus de la scène sans perdre le relief
   là où je regarde.

## Découpage

| # | Ticket | Dépend de | Statut |
|---|---|---|---|
| 01 | [BL-133](tickets/01-champ-de-vision-juste.md) — Le champ de vision par défaut, et son nom | — | ✅ |
| 02 | [BL-134](tickets/02-convergence-au-stick.md) — La convergence au stick, proportionnelle | — | ✅ |
| 03 | [BL-135](tickets/03-projection-bords-comprimes.md) — Voir plus large sans perdre le relief au centre | BL-133 | ✅ |

## Hors périmètre

- **Rapprocher les caméras en post-production** : demande une carte de
  profondeur par pixel calculée en temps réel. Écarté, voir ci-dessus.
- **Corriger un désalignement vertical entre les deux yeux.** Aucun réglage ne
  le fait aujourd'hui — la convergence ne joue que sur l'horizontale. Si un
  fichier s'avère décalé en hauteur, c'est un ticket à ouvrir, et l'observable
  qui le désigne est « ça tire vers le haut ou le bas » plutôt que « ça tire sur
  les côtés ».
