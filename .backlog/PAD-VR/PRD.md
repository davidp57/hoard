# Lot PAD-VR — Piloter le VR à la manette, en voyant ce qu'on règle

Status: ✅ done
Branch: `feature/pad-vr`

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
| 01 | [BL-127](tickets/01-fenetres-sbs.md) — Fenêtres manette lisibles en côte à côte | — | ✅ |
| 02 | [BL-128](tickets/02-couche-r2.md) — Couche VR sous R2 | — | ✅ |
| 03 | [BL-129](tickets/03-convergence-par-fichier.md) — Convergence retenue par fichier | BL-128 | ✅ |

## Vérifié sur le matériel (2026-09-21)

Essayé par David sur Deck + Beast après déploiement. **Deux corrections en ont
découlé**, livrées par la PR #62 :

- **La couche R2 ne répondait pas**, et la cause n'était pas dans Hoard : les
  détentes n'étaient plus mappées dans la configuration Steam du Deck, elles
  envoyaient des boutons de souris. Trouvé par David. Ce que le lot avait
  vraiment oublié, c'est que **le badge de couche n'affichait pas R2** — sans
  lui, une gâchette qui n'arrive pas ressemble à une gâchette qui arrive, et ça a
  coûté un aller-retour au lieu d'un coup d'œil.
- **Le stick droit regardait autour sans R2**, ce qui coûtait le volume pendant
  toute une lecture VR. Le regard passe sous la couche, le volume récupère son
  stick.

Et une leçon de méthode : les vérifications du lot passaient le modificateur
`r2` **à la main** à `_gpDispatch`. Elles seraient passées au vert avec une
manette débranchée. Elles passent désormais par une manette simulée rendue à
`navigator.getGamepads`.

**Ce que l'essai a révélé au-delà du lot** : les lunettes coupent l'image en deux
en permanence, donc toute l'interface est illisible, pas seulement pendant une
lecture. D'où le lot [PAD-SBS-UI](../PAD-SBS-UI/PRD.md).

## Hors périmètre

- **Les contrôles du lecteur, l'OSD de volume et le minuteur** restent masqués en
  côte à côte (décision de BL-120). Ils ne sont pas un chemin de pilotage : la
  manette et le clavier font tout ce qu'ils font.
- **La lecture immersive OpenXR** — écartée par [ADR 0003](../../docs/adr/0003-client-natif.md).
