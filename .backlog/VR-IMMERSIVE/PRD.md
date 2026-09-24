# Lot VR-IMMERSIVE — Le relief dans le casque, par WebXR

Status: 🧑 waiting-human
Branch: `feature/vr-immersive`

## Problem Statement

David a reçu son Steam Frame le 2026-09-24. Le mode 180° côte à côte n'y donne
aucun relief, et c'est logique : le navigateur du Frame est une fenêtre plate
posée dans l'espace, donc l'image côte à côte y arrive côte à côte, sur un seul
écran virtuel, vue par les deux yeux.

Les modes existants supposaient que l'affichage sépare lui-même les deux moitiés
(lunettes XR, téléviseur 3D). Un casque ne le fait pas : il faut que la page lui
donne une image par œil.

## Solution

Une session WebXR `immersive-vr`, ouverte depuis un bouton **XR** du lecteur. La
page prend le casque, dessine une image par œil, et la tête oriente la vue.

- Le rendu réutilise la déprojection existante (même texture, même contexte) ;
  seul change l'origine du rayon : la projection de chaque œil fournie par le
  casque et l'orientation de la tête, au lieu d'un sténopé centré piloté au stick.
- Orientation seulement, jamais la position : un film 180° est tourné d'un point
  unique, sa scène est à l'infini.
- Champ de vision, vue élargie et image étirée ne s'appliquent pas : le casque
  connaît son optique, la profondeur est juste d'office. La convergence du
  fichier, elle, s'applique.
- Commandes lues sur les manettes du casque, dans la session : gâchette et A/X
  lecture/pause, stick ←/→ du seek moyen, clic stick recentre, B/Y sort.

## Préalable non vérifié

**Le navigateur du Frame doit exposer WebXR.** Rien ne le garantit : Firefox l'a
abandonné, et Chromium sous Linux ne l'active pas partout. David a demandé de
coder en partant du principe que ça marche ; le lot attend son test.

Autre condition : WebXR n'existe que dans un contexte sécurisé. Hoard doit être
ouvert en **https**, sinon le bouton reste caché.

## Tickets

| Ticket | Statut |
|--------|--------|
| [BL-136](tickets/01-session-immersive.md) — Session immersive depuis le lecteur | 🧑 |
