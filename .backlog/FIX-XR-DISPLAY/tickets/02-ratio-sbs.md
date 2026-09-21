# BL-125 — Deviner la disposition côte à côte

Status: ⬜ ready
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

## Acceptance criteria

- [ ] À 3840×1080, l'image côte à côte a les bonnes proportions **sans réglage
      manuel**
- [ ] À une résolution 16:9, le comportement actuel est inchangé
- [ ] Un réglage explicite l'emporte sur la devinette, dans les deux sens
- [ ] La disposition retenue est visible par l'utilisateur (toast ou menu)
- [ ] La bascule est atteignable à la manette sans passer par deux menus
- [ ] Le bouton B de la manette garde son rôle actuel
- [ ] Vérifié sur le matériel réel (Deck + Beast) — ce qui ne peut pas être fait
      depuis un poste de bureau, comme pour FEAT-VR180

## Ce qu'il ne faut pas rater

Le ratio à tester est celui du **canvas**, pas celui de l'écran : en fenêtré, ou
avec une barre de navigateur, les deux diffèrent. Et le champ vertical est déjà
borné à 110° (`VR_MAX_VFOV`, ajouté par BL-119 après mesure) : vérifier que la
devinette n'entre pas en conflit avec ce plafond, qui réécrit `th` quand il
s'applique.
