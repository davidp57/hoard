# BL-145 — Service sur le casque pour revenir dans Hoard

Status: 🚫 wontfix (décision de David, 2026-11-14)
Lot: [FEAT-FPX-HANDOFF](../PRD.md)

## Quoi

À faire **seulement si** l'essai de BL-144 montre que le Frame ne ramène pas Chromium devant à la fermeture de la vidéo, ou que le lien `steam://` ne passe pas depuis Chromium.

Un petit service utilisateur sur le casque (systemd `--user`, installé par un script relu, sans `sudo`). Il écoute FPX en local sur le port 23554, et quand la vidéo se ferme, il remet Chromium au premier plan (par `steam steam://rungameid/<chromium>` ou équivalent, à mesurer). Si le lien `steam://` ne passe pas depuis Chromium, il met aussi FPX devant à l'ouverture.

## Critères d'acceptation

- [ ] Mécanisme de mise au premier plan mesuré sur le Frame avant d'écrire le service.
- [ ] Installation et désinstallation en une commande, documentées dans le guide.
- [ ] **Essai sur le Frame (David)** : lancer depuis Hoard, fermer la vidéo dans FPX, se retrouver dans Hoard.

## Résultat (2026-11-14)

- Le retour dans Chromium marche sans aide : fermer la vidéo dans FPX ramène sur Hoard.
- Sans lien `steam://`, rien ne ramène FPX devant quand il tourne déjà : Chromium reste affiché (essai de David, identifiant Steam vidé).
- Mesuré par SSH, en lecture seule : FPX est une application OpenXR qui n'apparaît pas parmi les fenêtres de gamescope (`GAMESCOPE_FOCUSABLE_WINDOWS` ne liste que Chromium). Pas de mise au premier plan par l'affichage : seul le client Steam repasse sur le jeu (dialogue « Reprendre le jeu »).
- Piste possible, non mesurée : le client Steam est lancé avec `-cef-enable-debugging` et expose ses pages sur `127.0.0.1:8080` ; un service sur le casque pourrait y demander la reprise de FPX. Repose sur l'interface interne de Steam, sans garantie d'une mise à jour à l'autre.

David a choisi de ne pas le faire : quand FPX tourne déjà, il passe dessus lui-même. Hoard cesse d'ouvrir le lien Steam dans ce cas (BL-146).
