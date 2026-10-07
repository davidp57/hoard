# Lot PAD-LEFT-HAND — La main gauche règle ce qu'on regarde

Status: 🔄 in-progress
Branch: `feature/pad-left-hand`

## Problem Statement

Les manettes du Steam Frame sont **deux manettes séparées**, une par main, que le système présente comme une seule manette ordinaire (David, 2026-10-07).
Avec la disposition actuelle, régler le volume demande la main droite (stick droit) ou la croix, et la vitesse un clic du stick droit : les deux mains sont sollicitées pour ce qui relève du seul « je regarde ».

## Solution

- **Main gauche = ce qu'on regarde** : stick ↕ volume, stick ↔ vitesse de lecture tant qu'il est tenu, croix = sauts.
- **Main droite = le reste** : A/B/X/Y, R1, R2, Start inchangés ; l'avance fine passe au stick droit ↔.
- Une **convention manette commune** avec PadView, recopiée dans chaque dépôt.

## Décisions (David, 2026-10-07)

1. Stick gauche ↔ : modification **linéaire** de la vitesse, milieu = 1×, gauche plus lent, droite plus vite, retour au lâcher. Ce n'est pas un retour rapide.
2. Croix : ←/→ ∓30 s, ↑ +60 s, ↓ **+15 s** (deux sauts en avant, voulu).
3. R3 ne sert plus à la vitesse.
4. Pas de fusion de plusieurs manettes : le Frame présente une seule manette.

## Tickets

| # | Ticket | Status |
|---|--------|--------|
| 01 | [BL-138 — Disposition main gauche du lecteur](tickets/01-left-hand-layout.md) | 🔄 |
| 02 | [BL-139 — Convention manette commune avec PadView](tickets/02-pad-convention.md) | 🔄 |
