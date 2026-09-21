# BL-126 — Fenêtres manette à l'échelle de l'écran

Status: ⬜ ready
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

## Acceptance criteria

- [ ] À 3840×1080, les deux fenêtres occupent une part de l'écran comparable à ce
      qu'elles occupent à 1920×1080, et leur texte est lisible
- [ ] **Le menu Select permet de basculer la disposition côte à côte sur le
      matériel réel** — c'est ce qui débloque BL-125
- [ ] À 1920×1080, rien ne change visuellement
- [ ] À 375 px de large, rien ne se dégrade : pas de débordement, pas de
      défilement horizontal
- [ ] Les deux fenêtres restent pilotables à la manette (curseur visible, D-pad,
      A, B) à toutes ces tailles
- [ ] Mesuré, pas jugé à l'œil : relever les tailles calculées aux trois largeurs

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
