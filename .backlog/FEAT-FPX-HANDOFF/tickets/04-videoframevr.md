# BL-155 — Lire aussi dans VideoFrameVR, et respecter le protocole DeoVR

Status: 🧑 waiting-human — livré en 2.9.12, reste l'essai sur le Frame avec VideoFrameVR (David)
Lot: [FEAT-FPX-HANDOFF](../PRD.md)

## Quoi

David a demandé une télécommande DeoVR à l'auteur de VideoFrameVR (seaweeduk/VideoFrameVR#109), un lecteur VR plus récent, centré sur la stéréo.
L'auteur l'a faite et l'a essayée contre Hoard `develop` `e153afa`.
Il signale deux écarts avec le vrai protocole DeoVR, vérifiés tous les deux :

1. DeoVR exige un paquet du client (vide ou JSON) chaque seconde, et coupe la connexion après 3 s de silence.
   Hoard n'envoyait que l'ouverture : la session finissait « déconnectée » pendant que la vidéo jouait.
2. Chez DeoVR, une trame vide du lecteur veut dire « rien d'ouvert » ; tant qu'une vidéo est ouverte, chaque état est du JSON, et `{}` n'est jamais envoyé.
   Hoard sautait les trames vides comme des pings : il ne voyait jamais la fermeture.

Conflit : FPX envoie une trame vide chaque seconde même vidéo ouverte, et `{}` quand rien ne l'est (sources de FPX, `crates/fp-remote/src/deovr.rs`, boucle de diffusion).
Prendre la trame vide pour une fermeture terminerait chaque session FPX au premier ping, et rien dans le trafic ne distingue les deux lecteurs.
Décision de David : un réglage « lecteur ».

## Réalisation (2026-11-25, 2.9.12)

- Heartbeat dans les deux modes : une trame vide toutes les `FPX_HEARTBEAT` (1 s) depuis le fil de lecture. FPX l'ignore. Un échec d'envoi termine la session en `disconnected`.
- Réglage `remote_player` (`fpx` par défaut, `deovr`). En `deovr`, une trame vide après l'ouverture confirmée termine la session en `closed`, même sauvegarde finale que `{}` ; avant l'ouverture, elle est ignorée. Mode `fpx` inchangé.
- Lancement : l'installeur de VideoFrameVR (`packaging/install/`) ajoute un raccourci non-Steam, par le client Steam ou en écrivant `shortcuts.vdf` (AppId `crc32(exe + nom) | 0x80000000`, le chemin de l'exécutable contient le dossier personnel). L'AppId dépend donc du compte : pas d'identifiant fixe à livrer. Nouveau réglage `deovr_steam_gameid`, ouvert par le même lien `steam://rungameid/` que FPX. Sans identifiant, l'écran dit de lancer le lecteur, et Hoard l'attend 20 s.
- Paramètres › « 🥽 Lecteur du casque » : choix du lecteur, l'identifiant Steam du lecteur choisi ; écran de lecture, toasts, menus manette et messages d'erreur nomment le lecteur.
- Vérifié par tests (heartbeat envoyé, échec d'envoi, `deovr` ferme sur trame vide après l'ouverture et l'ignore avant, `fpx` ignore les trames vides, réglages) et dans le navigateur avec des réponses simulées.

## Critères d'acceptation

- [x] Heartbeat envoyé chaque seconde pendant la session, dans les deux modes.
- [x] Mode `deovr` : trame vide après l'ouverture → `closed` avec sauvegarde ; avant l'ouverture → ignorée.
- [x] Mode `fpx` : comportement d'avant, réglage par défaut.
- [x] Lancement de VideoFrameVR par son identifiant Steam, ou message s'il manque.
- [ ] Essai sur le Frame avec VideoFrameVR : ouverture, suivi au-delà de 3 s, retour à la liste à la fermeture (David).
- [ ] Essai sur le Frame avec FramePlayerX : rien n'a changé, heartbeat compris (David).
