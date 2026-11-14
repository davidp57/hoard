# Lot FEAT-FPX-HANDOFF — Parcourir dans Hoard, lire dans FramePlayerX

Status: 🔄 in-progress

## Problem Statement

David, 2026-11-14, après l'essai de FEAT-HERESPHERE : l'API HereSphere marche, mais « ça ne fait pas ce que je veux ».
Depuis FramePlayerX (FPX), il voit ses vidéos, mais il ne voit pas l'arborescence de Hoard et ne peut rien effacer : « c'est vraiment pas pareil ».
Ce qu'il veut, c'est l'inverse : **parcourir avec Hoard**, et quand il lance une vidéo, **la lecture bascule automatiquement dans FPX**. En quittant FPX, **il revient dans Hoard**.

C'est la voie 1 notée le 2026-11-14 (note Obsidian « Hoard », section *Idées*).
FEAT-HERESPHERE reste en place : il ne gêne rien et sert à qui veut parcourir depuis FPX.

## Ce qui est établi (2026-11-14)

- **FPX a une télécommande DeoVR sur le port TCP 23554**, active par défaut, ouverte aux appareils du réseau local, sans appairage (guide FPX, section *Remote control* ; code `crates/fp-remote/src/deovr.rs`).
- **Format** : des messages préfixés par leur longueur sur 4 octets *little-endian*, suivis d'un JSON UTF-8 ; un message de longueur 0 est un *ping*. FPX envoie un ping environ toutes les secondes, et `{"path", "duration", "currentTime", "playbackSpeed", "playerState"}` (`playerState` 0 = lecture, 1 = pause) à chaque changement et au moins chaque seconde pendant la lecture. Il envoie `{}` quand rien n'est ouvert.
- **Commandes** : le client envoie la même forme avec un sous-ensemble des champs. Un `path` différent de la vidéo ouverte l'**ouvre** (`PlayerCommand::Open`), puis viennent la vitesse, `currentTime` (saut) et `playerState`. On peut donc ouvrir une vidéo **à la position de reprise** et lancer la lecture d'un seul message.
- **Mesuré** le 2026-11-14 depuis le PC de David, sans rien envoyer : connexion à `frame-david.lan:23554` acceptée, état reçu (vidéo ouverte, position, durée, pause). FPX écoute sur `0.0.0.0:23554`.
- **Authentification de l'adresse ouverte** : FPX transforme les identifiants écrits dans l'URL (`user:pass@`) en HTTP Basic (`fp-sources/src/http.rs`). On préfère une URL à jeton signé (décision 3) pour ne pas mettre le mot de passe dans l'adresse.
- **Raccourci Steam de FPX sur le Frame de David** : AppId `3052457826` (relevé par SSH, processus `reaper SteamLaunch AppId=…`). Pour un raccourci non-Steam, `steam://rungameid/` attend l'identifiant 64 bits `(AppId << 32) | 0x02000000`, soit `13110206535122812928`.
- **Inconnu, à mesurer dans le casque** : ce que fait le Frame quand Chromium ouvre un lien `steam://rungameid/…` alors qu'il tourne (FPX passe devant ? Chromium reste ouvert ?), et où l'on atterrit en quittant FPX. Une page web ne peut pas remettre Chromium au premier plan.
  David, 2026-11-14 : « implémente déjà ça, on verra si ça marche une fois implémenté ; de toute façon on n'a pas beaucoup d'autres solutions ».

## Solution

Le backend de Hoard, sur le NAS, parle à FPX par le port 23554 : il lui fait ouvrir la vidéo, suit la lecture et en reporte la position dans `progress`.
La page Hoard met FPX au premier plan par un lien `steam://`, affiche « Lecture dans FramePlayerX » tant que la vidéo est ouverte, et revient à la liste quand FPX signale la fermeture.
Le retour automatique vers Chromium dépend du comportement du Frame : BL-145 ne sera fait que si l'essai de BL-144 montre qu'il faut un service sur le casque.

**Essai du 2026-11-14** : lecture, reprise et retour dans Hoard marchent. Quand FPX tourne déjà, le lien `steam://` provoque l'erreur Steam « déjà lancé », et sans lui FPX reste derrière Chromium. BL-145 abandonné (voir le ticket) ; BL-146 n'ouvre le lien Steam que si FPX est fermé.

## Décisions (Claude, 2026-11-14 — valent par défaut)

1. **Réglages serveur** : `fpx_host` (nom ou IP du casque, vide par défaut = fonction coupée) et `fpx_steam_gameid` (identifiant 64 bits du lien `steam://rungameid/`, vide par défaut). Port fixe 23554. Le guide explique comment trouver les deux ; pour David : `frame-david.lan` et `13110206535122812928`.
2. **Bascule propre à l'appareil** : `localStorage['fpx_handoff']`. Elle n'a de sens que dans le casque : sur le PC ou le Deck, la lecture reste dans Hoard. C'est la quatrième clé de `localStorage` après `volume`, `sbs_global` et `gamepad_profile`, et donc une décision explicite, à noter dans la doc développeur. Elle s'active dans Paramètres, et le menu contextuel d'une vidéo garde « Lire ici » / « Lire dans FramePlayerX » pour faire l'exception.
3. **Adresse donnée à FPX = `/api/file` avec un jeton signé** dans la requête : HMAC avec `HOARD_SECRET_KEY`, lié au chemin et à une expiration (12 h), accepté **seulement** par `/api/file` en lecture. Jamais le mot de passe dans l'URL.
4. **Ouverture** : `POST /api/fpx/play {path}`. Le backend se connecte à `fpx_host:23554` (nouvel essai pendant ~20 s, le temps que FPX démarre), envoie `{"path": <url signée>, "currentTime": <reprise>, "playerState": 0}`, et garde la connexion. La page ouvre le lien `steam://` juste avant l'appel. Si FPX ne répond pas, erreur claire à l'écran (« FramePlayerX injoignable sur … ») et rien ne change.
5. **Suivi** : une session de suivi côté backend par lecture. Elle écrit la position dans `progress` toutes les 10 s, à la pause et à la fermeture, avec la règle « vu » existante (`watched_threshold`). Elle se termine quand FPX envoie `{}`, ouvre une autre adresse, ou coupe la connexion.
6. **Retour dans Hoard** : la page interroge `GET /api/fpx/status` (toutes les 1 à 2 s) pendant l'écran « Lecture dans FramePlayerX ». À la fin de la lecture, l'écran se ferme, la liste se rafraîchit, et le curseur reste sur la vidéo. Le bouton « Reprendre ici » (et B à la manette) abandonne le suivi et revient à la liste.
7. **Sécurité** : le backend ne se connecte qu'à `fpx_host`, sur le seul port 23554, et refuse une adresse qui n'est pas privée (RFC 1918, *link-local*, `.lan`, `.local`). Les nouvelles routes sont derrière l'authentification habituelle.

## Hors périmètre

- Changer FPX.
- Gérer les fichiers depuis FPX : on revient dans Hoard pour ça.

## Tickets

| # | Ticket | Status |
|---|--------|--------|
| 01 | [BL-144 — Lancer la lecture dans FramePlayerX depuis Hoard](tickets/01-handoff.md) | ✅ |
| 02 | [BL-145 — Service sur le casque pour revenir dans Hoard (si l'essai le montre nécessaire)](tickets/02-headset-helper.md) | 🚫 |
| 03 | [BL-146 — N'ouvrir le lien Steam que si FramePlayerX est fermé](tickets/03-steam-link-once.md) | 🧑 |
