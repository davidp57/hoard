# Lot FIX-UI-SCALE — Une taille apparente constante, quelle que soit la place

Status: 🧑 waiting-human (essai sur le Steam Frame)
Branch: `fix/ui-scale-viewport`

## Problem Statement

Dans le Chromium du Steam Frame, l'interface devient **très petite** quand le
navigateur passe en plein écran (constaté par David le 2026-09-29). Elle doit
garder une taille apparente constante, calculée **en proportion de l'espace
disponible** et non en pixels fixes.

Cause : toute l'interface était écrite en `px` (573 valeurs dans le CSS, plus
les styles en ligne). En plein écran, le navigateur annonce bien plus de pixels
CSS pour le même écran virtuel ; les mêmes pixels d'interface y occupent une
part plus petite.

## Solution

Une seule échelle, portée par la racine, et toutes les tailles en `rem` —
voir [BL-137](tickets/01-rem-scale.md).

## Décisions (David, 2026-09-29)

1. Conversion en `rem` plutôt que la propriété CSS `zoom` (mesurée : elle
   multiplie aussi `vw`/`dvh`).
2. Référence 1920×1080 : en dessous, la taille actuelle ; au-delà, croissance
   selon le plus petit des deux rapports.
3. Les fenêtres manette gardent leur croissance en largeur de BL-126, par-dessus
   la nouvelle échelle.

## Tickets

| # | Ticket | Status |
|---|--------|--------|
| 01 | [BL-137 — Toute l'interface en `rem`, une échelle à la racine](tickets/01-rem-scale.md) | ✅ |
