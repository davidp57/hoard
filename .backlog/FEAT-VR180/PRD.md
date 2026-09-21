# Lot FEAT-VR180 — Lecture des vidéos 180° SBS dans le lecteur web

Status: 🔄 in-progress
Branch: `feature/vr180`

## Problem Statement

Une partie de la médiathèque est constituée de vidéos **VR 180° stéréoscopiques
côte à côte** (SBS). Le lecteur les ouvre aujourd'hui comme n'importe quel fichier :
on voit les deux images accolées et écrasées, chaque œil déformé par la projection
équirectangulaire. Le fichier est lisible au sens technique, et inregardable au sens
réel.

Relevé fait sur un échantillon de 24 fichiers :

| | |
|---|---|
| Disposition | **SBS gauche/droite**, un œil = 180°×180° équirectangulaire |
| Ratio | 2:1 pour 23 fichiers sur 24 (l'œil est carré) ; un fichier en 3840×2160, donc œil 1920×2160 **anamorphosé** |
| Codec | 22 HEVC, 2 H.264 |
| Définition | 4600×2300 à **7680×3840**, tous à 60 fps, 30 à 47 Mbit/s |
| Métadonnées sphériques | **aucune** (ni `st3d` ni `sv3d`) |
| Audio | AAC stéréo — pas d'ambisonique |

Deux conséquences structurantes :

1. **Aucun fichier ne porte de métadonnée exploitable.** La détection ne peut
   s'appuyer que sur le ratio d'image et le nom, et doit rester rattrapable à la main.
2. **Le transcodage est hors de question.** `/api/transcode` tourne sur un NAS
   volontairement peu puissant ; 8K à 60 images par seconde n'y passera jamais. Le
   fichier est servi brut par `/api/file`, et **c'est la machine qui regarde qui doit
   décoder**. C'est la limite réelle du lot, et elle est extérieure au code écrit ici.

## Solution

Un **mode VR dans le lecteur web**, qui déprojette l'hémisphère en vue perspective.

Le `<video>` reste la source de vérité — lecture, position, progression, sous-titres,
pilotage : rien de tout cela ne change. Il devient seulement invisible, et un
`<canvas>` WebGL le recouvre et dessine ce qu'on regarde.

**Le rendu est un quad plein écran et un fragment shader**, pas un maillage de sphère.
Pour chaque pixel, on calcule la direction du rayon depuis le lacet, le tangage et le
champ de vision courants, on la convertit en coordonnée équirectangulaire, on
échantillonne la moitié d'image de l'œil visé. C'est exact, sans couture, et ça traite
le fichier anamorphosé sans cas particulier : le shader ne connaît que les bornes UV
de l'œil et l'angle couvert, pas la forme des pixels.

**Deux sorties, un seul shader.**

| mode | sortie | cible |
|---|---|---|
| `flat` | une vue, un œil | laptop tactile, iPad — et repérage |
| `sbs` | deux vues côte à côte, une par œil | **Steam Deck + lunettes Viture Beast**, qui font elles-mêmes la séparation stéréo |

La sortie `sbs` est la sortie `flat` dessinée deux fois dans deux moitiés d'écran, avec
l'autre œil en source. Il n'y a pas de parallaxe à calculer : chaque œil possède déjà
son propre hémisphère dans le fichier.

**WebXR est écarté de ce lot**, sans être condamné : le casque (Steam Frame) n'est pas
livré, donc une session immersive ne pourrait pas être vérifiée. Le shader étant le
même, l'ajouter plus tard coûtera peu.

## User Stories

1. En tant qu'utilisateur sur Steam Deck avec des lunettes XR, je veux que le lecteur
   sorte une image côte à côte déprojetée, pour regarder mes films 180° en relief.
2. En tant qu'utilisateur sur le laptop ou l'iPad, je veux une vue plate navigable,
   pour au moins pouvoir regarder et me repérer dans un fichier VR sans casque.
3. En tant qu'utilisateur, je veux regarder autour de moi au stick droit de la
   manette, sans lâcher la manette ni chercher une souris.
4. En tant qu'utilisateur, je veux que le lecteur reconnaisse seul mes fichiers VR, et
   que je puisse le corriger quand il se trompe, sans que le choix soit à refaire à
   chaque ouverture.
5. En tant qu'utilisateur, je veux régler le champ de vision et la sensibilité, parce
   que les studios ne cadrent pas pareil et que le confort n'est pas le même d'une
   machine à l'autre.

## Implementation Decisions

- **Shader plein écran plutôt que maillage sphérique.** Un maillage impose un
  compromis entre le nombre de facettes et la justesse aux pôles, et rend la
  déformation dépendante de la finesse du maillage. Le rayon par pixel n'a pas ce
  compromis, et le code est plus court.
- **`requestVideoFrameCallback` pour l'envoi de texture**, avec repli sur
  `requestAnimationFrame`. À 7680×3840 l'envoi de texture est le poste dominant ; il
  ne faut le payer qu'aux images réellement décodées, pas à chaque rafraîchissement
  d'écran.
- **Détection par ratio et par nom, jamais par transcodage.** Ratio 2:1 (ou
  16:9 avec un motif de nom) plus les motifs `_LR`, `3dh`, `180`, `SBS`, `VR180`,
  `oculusrift`. Vérifié : ces règles couvrent les 24 fichiers de l'échantillon.
- **Le mode retenu est mémorisé par fichier, côté serveur**, comme la progression —
  pas dans `localStorage`, qui ne suivrait pas d'une machine à l'autre.
- **En mode VR, le glissé d'un doigt regarde autour.** Il servait au seek et au
  volume ; ceux-ci restent accessibles au clavier, à la manette et aux boutons du
  lecteur, tous déjà câblés. Sans cet arbitrage, les deux usages se disputent le même
  geste.
- **Pas de WebXR dans ce lot** (voir ci-dessus).
- **Pas de transcodage VR** : le mode VR est refusé sur le flux `/api/transcode`, pour
  qu'un clic malheureux ne mette pas le NAS à genoux.

## Découpage

| # | Ticket | Dépend de | Statut |
|---|---|---|---|
| 01 | [BL-119](tickets/01-socle-deprojection.md) — Socle : déprojection, vue plate, pilotage | — | ✅ |
| 02 | [BL-120](tickets/02-sortie-sbs.md) — Sortie côte à côte pour lunettes XR | 01 | ✅ |
| 03 | [BL-121](tickets/03-detection-memorisation.md) — Détection des fichiers VR et mémorisation | 01 | ⬜ |
| 04 | [BL-122](tickets/04-reglages.md) — Réglages : champ de vision, convergence, sensibilité | 01, 02 | ⬜ |

Le ticket 01 était **une porte** : il mesurait sur les vrais fichiers ce que le
navigateur sait décoder et ce que l'envoi de texture coûte. **Elle est franchie** —
géométrie exacte au pixel, HEVC 7200×3600 à 60 images/s décodé sans perte, texture
16384 suffisante. La réserve tient : c'est mesuré sur un navigateur et une machine, et
la mesure sur le Steam Deck reste due.

## Hors périmètre

- **WebXR / session immersive** — le casque n'est pas livré, rien ne serait vérifiable.
- **Projections en œil-de-poisson** (MKX200 et apparentées) — aucun fichier de
  l'échantillon n'en relève. Le shader laisse la porte ouverte, le lot ne l'ouvre pas.
- **Disposition haut/bas** (over-under) — même raison.
- **Transcodage ou ré-encodage côté serveur** — le NAS ne peut pas, et le lot ne le
  demande pas.
- **Audio ambisonique** — les fichiers sont en stéréo.
- **Client natif** — explicitement mis de côté pour ce besoin.
