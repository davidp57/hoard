# Lot CLIENT-NATIVE — Client natif Flutter (Deck, Frame, Windows)

Status: 🔄 in-progress
Branch: `feature/client-native`
ADR: [0003 — Client natif](../../docs/adr/0003-client-natif.md)

## Problem Statement

Hoard se consulte depuis un navigateur. Sur **Steam Deck en mode Gaming**, cet usage se
dégrade au point de gêner l'usage quotidien :

- **La saisie au clavier ne fonctionne pas de façon fiable.** C'était le défaut
  principal, et l'hypothèse de départ le rattachait à un travers connu des applications
  non-Steam en mode Gaming
  ([steam-for-linux#9117](https://github.com/ValveSoftware/steam-for-linux/issues/9117)).
  **BL-104 a démenti cette hypothèse** : le défaut ne touche qu'Edge, `Steam+X`
  fonctionne dans une application native. Ce point reste la motivation historique du
  lot, mais il est résolu par le seul passage en natif.
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
2. **Un clavier à l'écran maison**, piloté à la manette — ~~parce que dépendre du
   clavier système reconduirait le défaut~~. Mesure faite (BL-104), le clavier système
   fonctionne : ce point devient un **confort** pour taper sans lâcher la manette, et
   non une nécessité.
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

Le ticket **01 était une porte** : il levait trois inconnues capables de remettre
en cause le lot. Il est rendu, et les tickets suivants sont rédigés à la lumière
de ce qu'il a mesuré.

| # | Ticket | Dépend de | Statut |
|---|---|---|---|
| 01 | [BL-104](tickets/01-faisabilite.md) — Faisabilité | — | ✅ |
| 02 | [BL-107](tickets/02-client-api.md) — Client d'API et modèle de données | 01 | ⬜ |
| 03 | [BL-108](tickets/03-navigation.md) — Navigation, états de lecture, tri, recherche | 02 | ⬜ |
| 04 | [BL-109](tickets/04-lecteur-video.md) — Lecteur vidéo : **trancher le chemin de rendu** | 02 | ⬜ |
| 05 | [BL-110](tickets/05-manette.md) — Manette : navigation et couches | 03, 04 | ⬜ |
| 06 | [BL-111](tickets/06-clavier-ecran.md) — Clavier à l'écran (déclassé, voir plus bas) | 05 | ⬜ |
| 07 | [BL-112](tickets/07-gestion-fichiers.md) — Gestion de fichiers | 03, 06 | ⬜ |
| 08 | [BL-113](tickets/08-galerie-archives.md) — Galerie d'images et archives | 03 | ⬜ |
| 09 | [BL-114](tickets/09-telechargements.md) — Téléchargements, segments, tags | 06 | ⬜ |
| 10 | [BL-115](tickets/10-reglages.md) — Réglages et verrou PIN | 06 | ⬜ |
| 11 | [BL-116](tickets/11-empaquetage.md) — Empaquetage : Flatpak, Windows, CI | 04 | ⬜ |
| 12 | [BL-117](tickets/12-arm64-frame.md) — Cible ARM64 et Steam Frame | 11 | 🧑 |

## Ce que la faisabilité a changé

**La motivation première du lot est tombée — dans le bon sens.** Le défaut de
saisie en mode Gaming ne touchait **qu'Edge** : `Steam+X` fonctionne dans une
application native sans rien faire de particulier. Le clavier maison (BL-111)
passe donc de nécessité à confort, et peut être déclassé voire écarté.

**Le décodage matériel n'était pas le problème non plus.** `hwdec=auto-safe`
donne `vaapi-copy`, à 102 % d'un cœur contre 118 % en logiciel. Forcer `vaapi`
est contre-productif : mpv retombe en logiciel, faute de partage GPU possible
avec la texture Flutter.

**Le vrai obstacle est le rendu.** `media_kit` ne signale pas ses nouvelles
images à Flutter : la vidéo n'avance que lorsque l'interface est repeinte pour
une autre raison — 8 images par seconde au repos, 25 dès qu'une animation
tourne. Ça ne remet pas Flutter en cause, mais **BL-109 devient le ticket
décisif du lot** et doit trancher entre laisser mpv dessiner sa propre surface
ou forcer le redessin, sur mesure et non sur le papier. BL-113 hérite de la même
question si la galerie passe aussi par une texture.

**L'empaquetage est cadré** : liste blanche mesurée sur la cible, et Flatpak
comme réponse durable (BL-116).

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
