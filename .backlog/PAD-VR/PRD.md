# Lot PAD-VR — Piloter le VR à la manette, en voyant ce qu'on règle

Status: ⬜ ready
Branch: `feature/pad-vr` (à créer)

## Problem Statement

Le lot [FIX-XR-DISPLAY](../FIX-XR-DISPLAY/PRD.md) est livré et vérifié sur le
matériel le **2026-09-21** : la devinette choisit `full` toute seule sur Deck +
Viture Beast, et c'est la bonne. Ce test a fait apparaître deux manques, tous
deux sur le **pilotage** et pas sur l'image.

1. **L'interface est illisible en mode côte à côte** — « compliquée à lire en
   mode SBS parce qu'elle ne l'est pas ». Le menu Select et la carte des boutons
   sont dessinés **une seule fois**, centrés, donc à cheval sur la coupure : chaque
   œil en voit une moitié. C'est le défaut que BL-120 avait contourné en masquant
   les contrôles, et que BL-125 a résolu **pour le seul toast**. Les deux fenêtres
   sont restées de côté parce que personne ne les avait regardées en SBS.

2. **La convergence ne se règle qu'à l'aveugle.** Le seul chemin est le menu
   Select, qui recouvre la vidéo : on change la valeur sans voir l'effet, on
   referme, on regarde, on rouvre. `vrAdjustConvergence()` existe dans le code —
   **et n'est appelée de nulle part**, c'est du code mort depuis BL-122. Le champ
   de vision n'a pas davantage de raccourci manette : seulement la molette de la
   souris, inutilisable sur un Deck.

## Solution

**Une couche VR sous R2**, la dernière gâchette libre, symétrique de L2 qui porte
déjà la bascule de disposition depuis BL-125. R2 maintenu, les deux sticks et
leurs clics pilotent la vue ; un modificateur maintenu rend tout déclenchement
accidentel impossible, ce qui compte pour un réglage qui, mal touché, fatigue les
yeux.

| Geste (R2 maintenu) | Action |
|---|---|
| Stick droit | Regarder autour (déjà le cas sans R2, conservé pour la cohérence) |
| **Stick gauche ↕** | **Zoom** (champ de vision) |
| **D-pad ←/→** | **Convergence** − / + |
| **Clic stick gauche (L3)** | **Remettre le zoom à zéro** |
| **Clic stick droit (R3)** | **Remettre le regard au centre** |

Cadrage arrêté avec David le 2026-09-21. `vrRecenter()` fait aujourd'hui les deux
remises à zéro d'un coup — elle est scindée, les deux gestes étant distincts.

**Et la convergence est retenue par fichier**, comme le mode VR l'est depuis
BL-121 : la gêne vient du tournage plus que des yeux, donc un fichier mal monté ne
doit pas contaminer les autres.

## User Stories

1. En tant qu'utilisateur sur Deck + Beast, je veux lire le menu Select en mode
   côte à côte, parce que c'est mon seul chemin vers les réglages.
2. En tant qu'utilisateur, je veux régler la convergence **en voyant l'image
   changer**, pas en ouvrant un menu qui la recouvre.
3. En tant qu'utilisateur, je ne veux pas refaire ce réglage à chaque ouverture
   d'un fichier qui en avait besoin.

## Découpage

| # | Ticket | Dépend de | Statut |
|---|---|---|---|
| 01 | [BL-127](tickets/01-fenetres-sbs.md) — Fenêtres manette lisibles en côte à côte | — | ⬜ |
| 02 | [BL-128](tickets/02-couche-r2.md) — Couche VR sous R2 | — | ⬜ |
| 03 | [BL-129](tickets/03-convergence-par-fichier.md) — Convergence retenue par fichier | BL-128 | ⬜ |

## Hors périmètre

- **Les contrôles du lecteur, l'OSD de volume et le minuteur** restent masqués en
  côte à côte (décision de BL-120). Ils ne sont pas un chemin de pilotage : la
  manette et le clavier font tout ce qu'ils font.
- **La lecture immersive OpenXR** — écartée par [ADR 0003](../../docs/adr/0003-client-natif.md).
