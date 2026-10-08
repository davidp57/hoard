# Lot PAD-ZOOM — Zoomer dans une vidéo à la manette, comme dans PadView

Status: 🔄 in-progress
Branch: `feature/pad-zoom`

## Problem Statement

David, 2026-10-08 : « je voudrais une fonction de zoom comme dans padview ».
PadView cadre une cam en maintenant R2 : stick gauche ↕ zoom, stick droit déplacement, L3 remise à zéro.
La convention manette commune ([`docs/pad-convention.en.md`](../../docs/pad-convention.en.md)) prévoit cette même couche de vue sous R2, mais Hoard ne l'appliquait qu'en mode VR : sur une vidéo ordinaire, R2 ne faisait rien.

## Solution

La couche R2 sur une vidéo plate, avec les mêmes gestes que PadView et que la couche VR de Hoard, et un encart de cadrage (niveau + mini-carte) tant que R2 est tenu.

## Décisions (David, 2026-10-08)

1. **Pas de mémorisation** : le zoom repart à 1× à chaque fichier. PadView mémorise par modèle parce qu'une cam se revoit ; un fichier se regarde une fois. Et `localStorage` est réservé aux réglages propres à l'appareil.
2. **Pas de plein écran obligatoire** : PadView en a besoin parce qu'il est injecté dans la page d'un autre site ; Hoard maîtrise son lecteur.
3. **Manette seulement** dans ce lot : la molette et les deux doigts ont déjà d'autres usages dans le lecteur.

## Tickets

| # | Ticket | Status |
|---|--------|--------|
| 01 | [BL-140 — Zoom et déplacement sous R2 sur une vidéo plate](tickets/01-flat-zoom.md) | 🔄 |
