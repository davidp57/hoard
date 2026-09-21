# BL-126 — Fenêtres manette à l'échelle de l'écran

Status: ✅ done
Type: fix
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

En 3840×1080 — la résolution qu'il faut pour obtenir le mode côte à côte sur les
Viture Beast — l'interface est trop petite, « en particulier la vue du bouton BACK
et celle du bouton START ». Ces fenêtres doivent s'adapter à la taille de l'écran.

Ce n'est **pas** un problème propre au VR : ces deux fenêtres servent partout dans
Hoard. C'est la résolution imposée par les lunettes qui l'a révélé. Le correctif
ne doit donc dégrader ni les résolutions ordinaires, ni le mobile.

## Diagnostic (mesuré sur le CSS livré)

Les deux fenêtres ne souffrent pas du même défaut, et ne se corrigent pas pareil.

| Élément | Déclaration actuelle | Ce qui cloche à 3840 |
|---|---|---|
| `#gp-menu-box` — menu contextuel (**Select**) | `width: 380px; max-width: 94vw; max-height: 86vh` | Largeur **fixe**. 380 px = **9,9 %** de la largeur à 3840, contre **19,8 %** à 1920 : deux fois plus petite en proportion. `max-width` est un plafond, il ne fait jamais grandir. |
| `#gp-overlay-box` — carte des boutons (**START**) | `width: 75vw; max-width: 98vw; max-height: 90vh` | La boîte **s'adapte déjà** (2880 px à 3840), mais son **contenu est en px fixes** : titre `15px`, onglets `11px`, sections `10px`. Une grande boîte remplie de texte minuscule. |

Le menu contextuel, lui, cumule les deux : boîte fixe **et** contenu fixe
(`.gp-menu-section` à `10px`).

## What to build

- **Le menu contextuel prend une largeur relative**, avec un plancher et un
  plafond en pixels pour ne pas devenir ridicule sur un téléphone ni immense sur
  un ultra-large. `clamp()` dit exactement ça en une déclaration.
- **La typographie des deux fenêtres suit la taille de l'écran.** Mesurer d'abord
  ce qui est lisible à 3840×1080 sur des lunettes — la distance apparente n'est
  pas celle d'un écran de bureau, donc la bonne valeur ne se déduit pas d'un
  calcul de proportion. À défaut d'accès au matériel, proposer une échelle et
  faire trancher par l'essai.
- **Vérifier les deux extrêmes**, pas seulement le cas qui a motivé le ticket :
  largeur téléphone (375 px, où `max-width: 94vw` fait le travail aujourd'hui) et
  3840 px. Une régression sur mobile serait un mauvais échange — Hoard sert aussi
  sur iPad.

## Ce ticket en débloque un autre

**BL-125 ne peut pas être testé avant celui-ci.** Le réglage de disposition côte à
côte ne s'atteint à la manette que par le menu Select — la fenêtre même qui est
illisible. `openSettings()` n'est appelé que depuis le bouton ⚙️ de l'en-tête
(`index.html:1818`) et depuis ce menu (`index.html:7112`) : il n'y a pas d'autre
chemin manette. Donc ce ticket passe en premier, et le critère « lisible à
3840×1080 » se mesure concrètement par *David arrive-t-il à basculer la
disposition depuis Select, sur son matériel*.

## Ce que la mesure a corrigé au diagnostic

Relevé dans le navigateur avant tout changement, aux trois largeurs. Le tableau
ci-dessus est juste pour le menu Select. **Il est faux pour la carte des boutons** :
sa boîte s'adapte bien, mais le dessin SVG qu'elle contient garde sa largeur
intrinsèque de **340 px à toutes les résolutions** — `width: auto` avec
`max-width: 100%` ne peut que rétrécir, jamais grandir. Ses libellés déclarés à
9 pt dans un `viewBox` de 540 étaient donc rendus à **5,7 px**, à 1920 comme à
3840, et à 4 px sur téléphone. Ce n'était pas « une grande boîte remplie de texte
minuscule » mais **une grande boîte contenant un petit dessin**, illisible partout.

Le critère « à 1920, rien ne change » était donc inapplicable à cette fenêtre :
elle était déjà défaillante à 1920. David a tranché le 2026-09-21 — **remplacer le
dessin par un écran texte**, comme le menu Select et comme l'aide manette du projet
PadView. Le dessin est supprimé.

## Ce qui a été fait

- `#gp-menu-box` : `width: clamp(380px, 19.79vw, 760px)` — strictement inchangé en
  dessous de 1920, proportion constante au-delà.
- **Une seule échelle typographique** pour les deux fenêtres,
  `clamp(13px, calc(6.5px + 0.339vw), 19.5px)`, toutes les tailles internes
  devenant des `em`. 13 px jusqu'à 1920, 19,5 px à 3840.
- **Le dessin SVG est remplacé par une liste texte** (`_gpRenderCtrl` supprimée,
  ~85 lignes), en colonnes qui coulent selon la largeur : 1 à 375, 4 à 1920,
  6 à 3840. Elle montre **toutes les couches à la fois** — le dessin n'en montrait
  qu'une, celle du modificateur physiquement tenu, d'où la disparition de la
  mécanique de re-rendu en direct (`_gpOverlayRerenderFn`, `_ovLb`, `_ovRb`).
- **Deux actions réapparaissent** : L3 (couper le son) et R3 (vitesse de lecture),
  que le dessin ne représentait pas. Les sticks suivent le réglage d'inversion,
  que le pied de page fixe ignorait.
- **Défilement au D-pad** dans la carte des boutons, qui n'acceptait que « fermer ».

## Trouvé par la revue avant la PR

- **Vocabulaire incohérent.** Le dessin nommait les gâchettes `LB` / `RB` ; le badge
  de couche affiche `🎮 L1` et les deux guides utilisateur parlent de L1 / R1. La
  liste s'aligne sur **L1 / R1**.
- **Le tableau des actions du lecteur est faux sur six cases**, dans les deux
  guides — et la nouvelle fenêtre le rend visible, puisqu'elle affiche les mêmes
  couches. L1+Y = marquer point IN (pas « aller à 0% ») ; R1+Y = confirmer segment
  OUT (pas rien) ; L1+R1 sur B / X / Y = supprimer / déplacer / exporter (pas des
  sauts de position) ; L1+R1+D↓ = aller à 100% ; et **Select ouvre le menu
  contextuel, pas les paramètres** — `player_base` surcharge `base` sur ce bouton
  depuis BL-086. Corrigé d'après le code dans `user-guide.fr.md` et `.en.md`.

## Relevé après correction

| | 375 px | 1920 px | 3840 px |
|---|---|---|---|
| Menu Select | 338 px | 380 px | 760 px |
| Texte du menu | 13 px | 13 px | 19,5 px |
| Carte des boutons | 338 × 731 px (défile) | 1440 × 456 px | 2880 × 631 px |
| Colonnes de la liste | 1 | 4 | 6 |
| Débordement horizontal | aucun | aucun | aucun |

À 3840, la carte tient dans 631 px sur les 972 disponibles, sans défilement.

## Acceptance criteria

- [x] À 3840×1080, les deux fenêtres occupent une part de l'écran comparable à ce
      qu'elles occupent à 1920×1080, et leur texte est lisible
- [ ] **Le menu Select permet de basculer la disposition côte à côte sur le
      matériel réel** — c'est ce qui débloque BL-125 *(à vérifier par David)*
- [x] À 1920×1080, rien ne change visuellement — **sauf la carte des boutons**,
      dont le dessin est remplacé par la liste texte (voir ci-dessus)
- [x] À 375 px de large, rien ne se dégrade : pas de débordement, pas de
      défilement horizontal
- [x] Les deux fenêtres restent pilotables à la manette (curseur visible, D-pad,
      A, B) à toutes ces tailles
- [x] Mesuré, pas jugé à l'œil : relever les tailles calculées aux trois largeurs

## Ce qu'il ne faut pas rater

**Le contenu de la carte des boutons est déjà long** : il liste toutes les actions
par couche, avec une barre d'onglets. Grossir le texte sans toucher à
`max-height: 90vh` le fera déborder en défilement vertical — ce qui, à la manette,
n'est pas gratuit : il faut que le curseur atteigne encore tous les éléments. Le
menu contextuel a le même risque (`max-height: 86vh`, `overflow-y: auto`).

**Les deux fenêtres passent en `position: absolute` en plein écran**
(`.in-fullscreen`, `index.html:843`), parce qu'elles sont déplacées dans l'élément
plein écran. Les unités relatives au viewport ne se réfèrent alors plus au même
rectangle : vérifier les deux états, fenêtré et plein écran.

**En mode côte à côte, ces incrustations sont masquées** (décision de BL-120 :
dessinées une fois sur une image coupée en deux, elles tombent à moitié dans
chaque œil). Le défaut signalé se voit donc en navigation ou en mode plat, pas
pendant la lecture côte à côte — ne pas chercher à le reproduire dans le mauvais
état.
