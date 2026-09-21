# BL-117 — Cible ARM64 et validation sur Steam Frame

Status: 🧑 waiting-human
Type: chore
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 11
Files: `client/`, `.github/workflows/`

## What to build

La cible **Linux ARM64** pour le Steam Frame (Snapdragon 8 Gen 3, SteamOS), et
la validation sur l'appareil.

Bloqué sur une ressource externe : le casque est commandé, pas encore livré.
**Blocage non bloquant** — le reste du lot avance sans lui.

Ce qui reste à mesurer là-bas, et qui ne se déduit pas du Deck :

- **Le décodage matériel sur GPU Adreno sous Linux.** Sur l'APU AMD du Deck,
  `vaapi-copy` fonctionne et coûte moins cher que le logiciel. Sur Adreno, le
  décodage vidéo sous Linux est historiquement partiel : à mesurer, pas à
  supposer.
- **La liste des bibliothèques absentes** est propre à l'architecture : elle
  sera différente, et c'est un argument de plus pour le Flatpak (BL-116).
- **Theatre Mode** projette toute application 2D sur un écran virtuel géant,
  sans travail spécifique. C'est le périmètre engagé ; la lecture immersive
  SBS 180°/360° reste hors lot (ADR 0003).

## Acceptance criteria

- [ ] Paquet ARM64 produit par la CI
- [ ] L'application tourne sur le Frame en Theatre Mode
- [ ] Décodage matériel mesuré sur l'appareil, avec et sans, sur le même fichier
