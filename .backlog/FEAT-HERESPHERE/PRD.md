# Lot FEAT-HERESPHERE — Lire les vidéos de Hoard dans FramePlayerX, par l'API HereSphere

Status: ⬜ ready

## Problem Statement

David, 2026-11-14 : [FramePlayerX](https://github.com/remotesojourner/frameplayerx) (FPX) tourne en natif sur le Steam Frame. Il décode en matériel le HEVC et le H.264 jusqu'en 8K, à 120 Hz, et il lit déjà le NAS en SMB.
Il règle ce que ni le lecteur WebGL de Hoard ni le client natif (ADR 0003, mis de côté) n'ont réglé : une lecture VR fluide et de qualité dans le casque.
Mais en SMB, FPX ne voit qu'une arborescence de fichiers. Il ignore ce que Hoard sait : ce qui est vu, ce qui est en cours, ce qu'on a regardé récemment, et le format VR réglé pour chaque fichier.

## Solution

Hoard **expose l'API HereSphere**, que FPX sait déjà lire (Sources › Add source › HereSphere), sans fork du lecteur.
Ça marcherait aussi avec HereSphere et DeoVR, qui parlent la même API.
Dans FPX, on voit les groupes de Hoard (en cours, récemment vus…), on lit, et les événements de lecture remontent dans `progress`.
La gestion des fichiers (déplacer, supprimer, renommer) reste dans l'interface web : l'API HereSphere ne la couvre pas.

Voie retenue par David le 2026-11-14, parmi trois (note Obsidian « Hoard », section *Idées*) :
1. Hoard pilote FPX par la télécommande DeoVR : Hoard reste l'interface, mais il faut tenir une connexion vers le casque.
2. Fork de FPX avec une source « Hoard » : le plus complet, mais un fork en Rust à maintenir.
3. **Hoard expose l'API HereSphere** : rien à maintenir côté lecteur.

## Contrat, relevé dans le code de FPX (v0.18, 2026-11-14)

Source : `crates/fp-sources/src/feed/heresphere.rs`, `feed/mod.rs`, `watch.rs` et `http.rs` du dépôt FPX.

- **Toutes les requêtes sont des `POST`** avec un corps JSON, qui contient `username` et `password` quand la source a des identifiants.
- **FPX envoie aussi ces identifiants en HTTP Basic** sur chaque requête vers l'origine de la source (`HttpClient::new` + `scoped_to`). Le middleware de Hoard, qui accepte cookie **ou** Basic, n'a donc rien à changer. FPX n'envoie pas d'en-têtes `Sec-Fetch-*`, donc le refus des écritures cross-site ne devrait pas le gêner (à confirmer par un test).
- **Bibliothèque** (l'URL saisie dans FPX) : `{"access": 1, "library": [{"name": "…", "list": ["<url de scène>", …]}]}`. `access` négatif = refus d'accès.
- **Scan** (`<url de la bibliothèque>/scan`, facultatif) : `{"scanData": [{"link", "title", "duration", "dateReleased", "dateAdded", "rating", "isFavorite", "tags": [{"name"}]}]}`. Il donne le détail de toutes les scènes en une requête ; sans lui, FPX ouvre chaque scène une par une. Durée en secondes ou en millisecondes : FPX tranche à 86 400.
- **Scène** (chaque URL de `list`) : `title`, `duration` (ms), `thumbnailImage`, `projection` (`equirectangular`, `equirectangular360`, `fisheye`, `perspective`…), `stereo` (`sbs`, `tb`, `mono`), `fov`, `lens`, `media: [{"name", "sources": [{"url", "resolution", "height", "width", "size"}]}]`, `tags: [{"name", "start", "end"}]`, `isFavorite`, `writeFavorite`, `eventServer`, `subtitles`. Le corps de la requête porte `needsMediaSource` (bool).
- **Événements de lecture** : `POST` sur `eventServer` avec `{"username", "id": <url de la scène>, "title", "event": 0 ouverture | 1 lecture | 2 pause | 3 fermeture, "time": <ms>, "speed", "utc": <ms>, "connectionKey": ""}`. Pas d'événement périodique : la position arrive à la pause, à la reprise, au saut et à la fermeture.
- **Favori** : `POST` sur l'URL de la scène avec `{"isFavorite": bool, "needsMediaSource": false}`, seulement si la scène a annoncé `writeFavorite: true`.
- **Ce que FPX ne lit pas** : aucune position de reprise venant du serveur (pas de `currentTime` dans le format HereSphere de FPX). FPX garde sa propre reprise sur le casque. Hoard reçoit la position du casque, mais ne peut pas lui envoyer celle d'un autre appareil.

## Décisions (Claude, 2026-11-14 — valent par défaut)

1. **Préfixe `/heresphere`** : bibliothèque `POST /heresphere`, scan `POST /heresphere/scan`, scène `POST /heresphere/scene/<id>`, événements `POST /heresphere/events`. Hors de `/api` : ce sont des routes pour un client tiers, avec leur propre format.
2. **Identifiant de scène = chemin relatif encodé en base64url.** Stable, sans table nouvelle, et `safe_path()` s'applique au décodage comme partout. Un fichier renommé ou déplacé change d'identifiant, comme dans `progress`, qui est indexé par le chemin.
3. **Groupes** : « En cours » (progression entamée, non vue), « Récemment vus » (par `progress.updated_at` décroissant), « Non vus » des dossiers rapides, puis un groupe par dossier rapide. Pas de groupe « tout le NAS » : parcourir tout `MEDIA_ROOT` à chaque ouverture coûte trop cher au NAS.
4. **Le média est servi par `GET /api/file`**, qui gère déjà les requêtes `Range`, sans transcodage : FPX décode lui-même le HEVC et le H.264. Une seule source par scène.
5. **Format VR** : le mode réglé pour le fichier (`vr_modes`) prime, sinon la détection par le nom déjà utilisée par le lecteur web. 180° SBS → `equirectangular` + `sbs` + `fov` 180 ; plat → `perspective` + `mono`.
6. **Événements → `progress`** : chaque événement 1, 2 ou 3 écrit la position. La règle « vu » existante (`watched_threshold`, 90 % par défaut) s'applique. `updated_at` suit, donc le tri « Vu » du web et le groupe « Récemment vus » aussi.
7. **Pas de favori ni de vignette dans un premier temps** : `writeFavorite` absent et pas de `thumbnailImage`. FPX fait ses vignettes sur le casque quand le serveur n'en donne pas.

## Hors périmètre

- Déplacer, supprimer, renommer depuis FPX : l'API ne le prévoit pas.
- Faire reprendre FPX à la position d'un autre appareil : FPX ne lit pas de reprise côté serveur.
- Tout changement dans FPX.

## Tickets

| # | Ticket | Status |
|---|--------|--------|
| 01 | [BL-142 — Bibliothèque, scan et scènes HereSphere](tickets/01-library.md) | ⬜ |
| 02 | [BL-143 — Événements de lecture vers `progress`](tickets/02-events.md) | ⬜ |
