# Lot PAD-PROFILES — Des profils de manette, dont un pour la seule main droite du Steam Frame

Status: 🧑 waiting-human (essai sur le Frame avec la seule manette droite)
Branch: `claude/steam-deck-controller-mapping-dd5b61`

## Problem Statement

David, 2026-11-05 : un soir, avec la seule manette droite du Steam Frame, il a pu piloter Hoard dans Chromium.
Mais le mapping est conçu pour les deux mains (lot PAD-LEFT-HAND) : sans la main gauche, pas de croix, pas de stick gauche, pas de L1 ni de Select, donc ni curseur dans la liste, ni menu, ni volume, ni vitesse.

## Solution

Des **profils**, à choisir selon ce qu'on a sous la main :

- **Standard (deux mains)** : le mapping existant, inchangé.
- **Steam Frame, main droite seule** : les commandes principales sur A, B, X, Y, R1, R2, le stick droit et son clic (R3).

## Décisions (David, 2026-11-05)

1. **Profil propre à l'appareil** (`localStorage['gamepad_profile']`) : choisir la main droite sur le Frame ne doit pas changer le Deck.
2. **Sous R1, le stick fait les sauts** de la croix du profil Standard (← −30 s, → +30 s, ↑ +60 s, ↓ +15 s).
3. **Y = menu dans la liste, plein écran dans le lecteur.** Le menu ne sert à rien dans le lecteur ; vu / non vu, muet et fichier précédent / suivant ne valent pas un bouton.
4. **Le mapping personnalisé (`gamepad_mapping`) ne s'applique qu'au profil Standard**, pour qu'un remplacement ne puisse pas retirer le menu au profil main droite.
5. **Stick ↔ = vitesse tant que tenu** dans le lecteur, ↕ = volume ; pas d'avance fine.
6. **R1 + X déplacer, R1 + B supprimer**, dans la liste comme dans le lecteur.
7. **R3 = Fit / Fill** dans le lecteur ; **R2 + R3 = revenir à 1×** (recentrer en VR, et R1 + R2 + R3 remet le zoom VR) ; **R1 + R2 + stick ↕ = zoom**.
8. **Le stick remplace la croix dans toutes les fenêtres** (menu, déplacer, supprimer, réglages, aide…) : choisir, A valide, B annule.

## Tickets

| # | Ticket | Status |
|---|--------|--------|
| 01 | [BL-141 — Profil « Steam Frame, main droite seule »](tickets/01-frame-right.md) | 🧑 |
