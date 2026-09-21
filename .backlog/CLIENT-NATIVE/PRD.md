# Lot CLIENT-NATIVE — Client natif Flutter (Deck, Frame, Windows)

Status: ⬜ ready
Branch: `feature/client-native` (à créer)
ADR: [0003 — Client natif](../../docs/adr/0003-client-natif.md)

## Problem Statement

Hoard se consulte depuis un navigateur. Sur **Steam Deck en mode Gaming**, cet usage se
dégrade au point de gêner l'usage quotidien :

- **La saisie au clavier ne fonctionne pas de façon fiable** — c'est le défaut
  principal. Une application non-Steam en mode Gaming ouvre le clavier *du bureau* au
  lieu de celui du mode Gaming, ce qui peut bloquer
  ([steam-for-linux#9117](https://github.com/ValveSoftware/steam-for-linux/issues/9117)).
  Sans saisie, la recherche, le renommage, les tags et la création de dossiers sont hors
  d'atteinte.
- **Le moteur web décode mal.** Les formats qu'un navigateur refuse (HEVC, certains
  MKV, pistes AC3/DTS, sous-titres ASS) obligent à passer par `/api/transcode`, qui
  charge un NAS volontairement peu puissant. Quand le décodage matériel n'est pas
  disponible, la lecture coûte ventilateur et batterie.
- Divers désagréments mineurs propres au navigateur (barres, plein écran, veille).

Le besoin s'étend désormais à trois machines : le Deck (x86_64), le **Steam Frame**
(ARM64, commandé) et le laptop Windows tactile.

## Solution

Un **client natif Flutter** qui consomme l'API HTTP existante. Le serveur ne change pas :
`/api/file` sert déjà le fichier brut avec `Range`, donc **libmpv** lit directement, sans
transcodage.

Trois choix structurants, détaillés et argumentés dans l'[ADR 0003](../../docs/adr/0003-client-natif.md) :

1. **Flutter + `media_kit`** (qui embarque libmpv), compilé nativement x86_64, ARM64 et
   Windows. Écartés : un binaire Windows sous Proton, Tauri, Rust/Slint, Kodi.
2. **Un clavier à l'écran maison**, piloté à la manette. Le défaut visé touche les
   applications non-Steam en général : dépendre du clavier système le reconduirait.
3. **Distribution par Flatpak**, parce que SteamOS est en lecture seule — et parce que
   `media_kit` ne livre pas de libmpv précompilé pour Linux
   ([#638](https://github.com/media-kit/media-kit/issues/638)), le paquet embarque la sienne.

Le **Steam Frame** est couvert sans travail spécifique : son *Theatre Mode* projette
toute application 2D sur un écran virtuel géant. La lecture de films **SBS 180°/360°**
est un besoin reconnu mais **hors de ce lot** : elle demande un rendu OpenXR stéréo,
hors de portée de Flutter, et fera l'objet d'une application séparée.

L'interface web **reste maintenue** : elle sert l'iPad et tout navigateur, et demeure le
seul accès tant que le client ne couvre pas le périmètre.

## User Stories

1. En tant qu'utilisateur sur Deck en mode Gaming, je veux saisir du texte de façon
   fiable (recherche, renommage, tags), pour ne plus être bloqué par le clavier système.
2. En tant qu'utilisateur, je veux que la lecture utilise le décodage matériel de la
   machine et accepte tous mes formats, pour ne plus solliciter le NAS ni vider la
   batterie.
3. En tant qu'utilisateur, je veux piloter toute l'application à la manette, sans
   jamais avoir besoin d'une souris ni d'un clavier physique.
4. En tant qu'utilisateur du Steam Frame, je veux retrouver Hoard sur un écran virtuel
   géant, sans installation particulière.
5. En tant qu'utilisateur du laptop Windows tactile, je veux la même application, avec
   les gestes tactiles.
6. En tant qu'utilisateur, je veux que ma progression reste partagée entre le client
   natif et l'interface web, pour reprendre une lecture d'un appareil à l'autre.

## Découpage

Le ticket **01 est une porte** : il lève trois inconnues qui peuvent remettre en cause
le reste du lot. Les tickets 02 et suivants ne sont donc **pas encore rédigés en
détail** — ils le seront une fois 01 rendu, à la lumière de ce qu'il aura mesuré.

| # | Ticket | Dépend de |
|---|---|---|
| 01 | Faisabilité : socle, libmpv, décodage matériel, clavier | — |
| 02 | Client d'API et modèle de données | 01 |
| 03 | Navigation : dossiers, états de lecture, tri, recherche | 02 |
| 04 | Lecteur vidéo : mpv, progression, sous-titres, gestes | 02 |
| 05 | Manette : navigation et 4 couches de boutons | 03, 04 |
| 06 | Clavier à l'écran piloté à la manette | 05 |
| 07 | Gestion de fichiers : déplacer, supprimer, renommer, dossiers rapides | 03, 06 |
| 08 | Galerie d'images et archives | 03 |
| 09 | Téléchargements, segments, tags | 06 |
| 10 | Réglages et verrou PIN | 06 |
| 11 | Empaquetage : Flatpak x86_64, Windows, CI | 04 |
| 12 | Cible ARM64 et validation sur Steam Frame | 11 |

## Hors périmètre

- **Lecture VR immersive** (SBS 180°/360°) — application séparée, voir ADR 0003.
- **Cible iPad** — possible avec Flutter, non engagée.
- **Modification du serveur** — le lot consomme l'API telle quelle. Tout besoin
  d'évolution d'API découvert en route fait l'objet d'un ticket distinct.
- **Retrait de l'interface web** — elle reste la référence fonctionnelle.

## Conséquences sur le dépôt

- Nouveau répertoire `client/`.
- `CLAUDE.md` : les règles « no build step » et « frontend en fichier unique » ne
  valent plus que pour `frontend/` — à amender.
- CI : compilation Flutter ajoutée, durée en minutes plutôt qu'en secondes.
- Le client porte sa **propre version**, indépendante de `pyproject.toml`, et vérifie au
  démarrage la version d'API du serveur.
