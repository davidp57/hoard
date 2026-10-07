# BL-138 — Disposition main gauche du lecteur

Status: 🔄 in-progress

## Quoi

| Commande | Avant | Après |
|---|---|---|
| Stick gauche ↕ | — | volume |
| Stick gauche ↔ | scrub | vitesse tant que tenu (0,25× ← 1× → 4×, 2× en transcodage) |
| Stick droit ↔ | — | scrub |
| Stick droit ↕ | volume | — |
| Croix ↑ / ↓ | volume ±10 % | +60 s (`seek_long`) / +15 s (fixe) |
| R3 | cycle de vitesse | libre |

*Inverser les sticks* échange les deux sticks en entier.
Sous R2 en mode VR, tous les sticks restent à la vue.

## Bornes de vitesse

- Linéaire **de chaque côté** de 1× : une seule droite passant par 1× donnerait 0,25×..1,75× ou −2×..4×.
- 4× au maximum, 2× sur une vidéo transcodée : le NAS encode en temps réel.
- Pas de 0,05× : un stick ne revient jamais parfaitement immobile.
- Au lâcher, retour à la vitesse en vigueur **avant** le stick (1×, ou celle choisie au menu Select).

## Vérification

Manette simulée rendue à `navigator.getGamepads`, boucle de scrutation réelle (pas d'appel direct à `_gpDispatch`).
