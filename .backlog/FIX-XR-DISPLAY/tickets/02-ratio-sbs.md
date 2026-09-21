# BL-125 — Deviner la disposition côte à côte

Status: ✅ done
Type: fix
Files: `frontend/index.html`, `tests/test_api.py` (si un réglage change),
`docs/user-guide.*.md`, `docs/developer.*.md`

## Problem

Sur Deck + Viture Beast en 3840×1080, l'image du mode côte à côte a de mauvaises
proportions : « les personnages sont trop hauts et trop étroits ». Constaté le
2026-09-21 sur le matériel réel — la vérification que FEAT-VR180 laissait due.

## Bloqué par BL-126

L'essai qui trancherait ce ticket n'est pas faisable aujourd'hui : à la manette, la
bascule de disposition ne s'atteint que par le menu Select, et c'est précisément la
fenêtre illisible que corrige [BL-126](01-ui-resolution.md). Faire BL-126 d'abord.

## À vérifier d'abord

**Passer le réglage sur « non étirée » corrige-t-il le ratio ?**
Select → « 🥽 Image côte à côte », ou Paramètres → Player → image étirée /
non étirée. Le diagnostic ci-dessous vient de la lecture du code, pas d'un essai.
**S'il est faux, ce ticket change de forme** : le défaut serait dans le calcul du
champ de vision et non dans la valeur du réglage.

## Diagnostic (lecture du code, à confirmer)

`frontend/index.html:5701` :

```js
const perceivedW = !sbs ? w : (vr.sbsLayout === 'half' ? w : w / 2);
let th = tanH, tv = tanH * vh / perceivedW;
```

- `half` suppose que l'afficheur réétire chaque moitié sur toute la largeur : la
  forme perçue est celle du canvas entier.
- `full` suppose qu'il n'en fait rien : chaque moitié est déjà au bon ratio.

À 3840×1080 en `half` (le défaut), `tv` est calculé depuis `1080/3840` au lieu de
`1080/1920` : le champ vertical est deux fois trop étroit, donc l'image est zoomée
verticalement — trop haute, trop étroite. C'est le symptôme décrit.

Or **3840×1080 est du full-SBS** : chaque moitié fait 1920×1080, au bon ratio, et
les Beast ne réétirent rien.

## What to build

- **Déduire la disposition du ratio du canvas** quand l'utilisateur n'a rien
  choisi explicitement : un canvas dont le ratio est proche de **deux fois** celui
  d'un affichage normal (32:9 pour du 16:9) est du `full` ; un ratio normal est du
  `half`. Mesurer le ratio réel du canvas sur l'appareil avant de figer le seuil —
  la fenêtre du navigateur n'occupe pas forcément tout l'écran.
- **Le réglage explicite reste prioritaire**, y compris quand il contredit la
  devinette — **tranché par David le 2026-09-21** : la devinette ne s'applique
  qu'en l'absence de choix enregistré, et ne l'écrase jamais. Même règle que
  `vr_mode` face à `vr_hint` dans FEAT-VR180 : une détection fausse doit être
  corrigeable, pas définitive.
- **Dire ce qui a été deviné.** Le basculement affiche déjà un toast
  (`index.html:5743`) ; la devinette doit être aussi lisible, sinon l'utilisateur
  ne peut pas savoir pourquoi son image change.
- **Un raccourci manette pour basculer.** Aujourd'hui le raccourci direct est la
  **touche B du clavier** (`index.html:6997`) — inutilisable sur un Deck, qui est
  la machine visée. À la manette il faut passer par Select puis l'entrée du menu,
  pour un réglage dont l'effet se voit instantanément à l'écran. Le **bouton B de
  la manette est déjà pris** (« annuler / fermer » partout) : ne pas le
  réutiliser, trouver un geste libre dans la couche de lecture.

## Ce qui a été fait

- **La disposition se déduit de la forme du canvas** (`vrResolvedSbsLayout`), avec
  un seuil à **2,4**. Le raisonnement : la forme perçue par chaque œil doit
  ressembler à un écran (4:3 à 21:9, soit 1,3 à 2,1) ; en `half` c'est le canvas
  entier, en `full` une moitié. Un canvas 16:9 (1,78) tombe donc en `half`, un
  32:9 (3,56) en `full`, chacun loin de la frontière — 2,4 est entre les deux
  bandes admissibles et dans aucune.
- **Le réglage gagne une valeur `auto`, qui devient le défaut.** Sans elle, rien
  ne distinguait « pas de choix » de « choix `half` » : les deux valaient `half`.
- **Une migration ponctuelle efface au démarrage une ligne `vr_sbs_layout` valant
  `half`**, et c'est ce qui rend le correctif effectif. Le formulaire de réglages
  poste tous ses champs, donc enregistrer n'importe quel réglage écrivait l'ancien
  défaut dans la table, où il se serait lu comme un choix délibéré. Tranché par
  David le 2026-09-21. À retirer une fois toutes les instances redémarrées.
- **Le toast est écrit une fois par œil** (25 % et 75 %). Voir ci-dessous : il
  était purement et simplement invisible en mode côte à côte.
- **Raccourci manette : L2**, libre dans toutes les couches — base, lecteur, L1,
  R1, L1+R1, browser — vérifié une par une. `B` garde son rôle d'annulation. Le
  cycle couvre les trois états, sinon `auto` deviendrait injoignable après une
  correction manuelle. Conditionné à `vrIsActive()` et non au seul mode côte à
  côte, comme le clavier : `setVrMode` ne réinitialise la disposition qu'en
  venant de `off`, donc la régler en mode plat avant de basculer est un usage réel.

## Ce que la vérification a corrigé au ticket

**Le toast n'était pas visible en mode côte à côte**, contrairement à ce
qu'affirmait ce ticket (« le basculement affiche déjà un toast »). BL-120 masquait
`#toast` avec les autres incrustations — `index.html:362` — pour la bonne raison
qu'une incrustation dessinée une fois sur une image coupée en deux tombe à moitié
dans chaque œil. Le critère « la disposition retenue est visible par l'utilisateur »
était donc intenable en l'état, et le toast de BL-120 lui-même ne servait à rien.
Corrigé à la cause : deux nœuds, un par œil, chacun centré dans sa moitié. Aucun
changement de taille — à 3840×1080 chaque moitié fait 1920 de large, donc 13 px
s'y lit comme sur un écran ordinaire. Les contrôles, l'OSD de volume et le
minuteur restent masqués : ils ne sont pas le moyen par lequel le lecteur dit ce
qu'il vient de faire.

## Mesuré

| forme du canvas | ratio | disposition |
|---|---|---|
| 1920×1080, 1280×720, 3840×2160 | 1,78 | `half` |
| 2560×1080 | 2,37 | `half` |
| 3840×1080 | 3,56 | `full` |
| 1080×1920 | 0,56 | `half` |
| 0×0 (canvas pas encore dimensionné) | — | `half` |

Vérifié de bout en bout sur un vrai rendu WebGL, vidéo à bandes horizontales : les
pixels lus diffèrent entre `half` et `full`, donc c'est bien le champ de vision
qui change. Un `half` forcé sur un canvas 32:9 reste `half`. Le cycle L2 parcourt
`auto → half → full → auto`. La migration a été éprouvée sur la base de dev réelle :
la ligne `half` a disparu au redémarrage, `vr_fov` et les autres sont intacts.

Le plafond `VR_MAX_VFOV` n'entre pas en conflit : à 3840×1080 il ne s'applique
dans aucun des deux cas (champ vertical de 31° en `half`, 59° en `full`, contre un
plafond à 110°).

## Acceptance criteria

- [x] À 3840×1080, l'image côte à côte a les bonnes proportions **sans réglage
      manuel**
- [x] À une résolution 16:9, le comportement actuel est inchangé
- [x] Un réglage explicite l'emporte sur la devinette, dans les deux sens
- [x] La disposition retenue est visible par l'utilisateur — toast **et** menu
      contextuel, tous deux marquant explicitement l'état « auto »
- [x] La bascule est atteignable à la manette sans passer par deux menus (L2)
- [x] Le bouton B de la manette garde son rôle actuel
- [ ] Vérifié sur le matériel réel (Deck + Beast) — ce qui ne peut pas être fait
      depuis un poste de bureau, comme pour FEAT-VR180 *(reste dû par David)*

## Ce qu'il ne faut pas rater

Le ratio à tester est celui du **canvas**, pas celui de l'écran : en fenêtré, ou
avec une barre de navigateur, les deux diffèrent. Et le champ vertical est déjà
borné à 110° (`VR_MAX_VFOV`, ajouté par BL-119 après mesure) : vérifier que la
devinette n'entre pas en conflit avec ce plafond, qui réécrit `th` quand il
s'applique.
