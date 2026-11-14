# BL-145 — Service sur le casque pour revenir dans Hoard

Status: 🧑 waiting-human (attend l'essai de BL-144 sur le Frame)
Lot: [FEAT-FPX-HANDOFF](../PRD.md)

## Quoi

À faire **seulement si** l'essai de BL-144 montre que le Frame ne ramène pas Chromium devant à la fermeture de la vidéo, ou que le lien `steam://` ne passe pas depuis Chromium.

Un petit service utilisateur sur le casque (systemd `--user`, installé par un script relu, sans `sudo`). Il écoute FPX en local sur le port 23554, et quand la vidéo se ferme, il remet Chromium au premier plan (par `steam steam://rungameid/<chromium>` ou équivalent, à mesurer). Si le lien `steam://` ne passe pas depuis Chromium, il met aussi FPX devant à l'ouverture.

## Critères d'acceptation

- [ ] Mécanisme de mise au premier plan mesuré sur le Frame avant d'écrire le service.
- [ ] Installation et désinstallation en une commande, documentées dans le guide.
- [ ] **Essai sur le Frame (David)** : lancer depuis Hoard, fermer la vidéo dans FPX, se retrouver dans Hoard.
