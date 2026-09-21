# BL-127 — Fenêtres manette lisibles en côte à côte

Status: ✅ done
Type: fix
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

En mode côte à côte, le menu Select (`#gp-menu`) et la carte des boutons
(`#gp-overlay`) sont dessinés **une seule fois**, centrés sur le conteneur, donc à
cheval sur la coupure entre les deux yeux. Chacun n'en voit qu'une moitié.
Constaté par David sur Deck + Beast le 2026-09-21 : « compliquée à lire en mode
SBS parce qu'elle ne l'est pas ».

Vérifié dans le code : la règle `#video-container.vr-sbs` (`index.html:362`) masque
`#controls`, `#vol-osd` et `#mini-time`, **mais pas** `#gp-menu` ni `#gp-overlay`.
Ils s'affichent donc, et mal.

## What to build

La technique est déjà éprouvée dans le dépôt : BL-125 a fait exactement ça pour le
toast, avec un second nœud (`#toast-r`) placé à 75 % pendant que l'original passe
à 25 %. Appliquer le même principe aux deux fenêtres.

- **Une copie par œil**, chacune centrée dans sa moitié. La copie de droite est
  **purement visuelle** : le curseur manette, les clics et le défilement
  continuent de porter sur l'originale.
- Les deux fenêtres construisent déjà leur contenu en une passe
  (`_gpMenuRender()`, `openGpOverlay()`) — il suffit de le poser dans deux boîtes.
  Ne pas dupliquer la logique, seulement le rendu.
- **La copie ne doit pas être lue deux fois** par une synthèse vocale ni recevoir
  le focus : `aria-hidden` et `inert` sur le miroir.
- Hors mode côte à côte, **rien ne change** : la copie n'existe pas.

## Acceptance criteria

- [ ] En mode côte à côte, le menu Select est lisible **dans chaque œil**
- [ ] Idem pour la carte des boutons
- [ ] Le curseur manette, A, B et le défilement D-pad marchent comme avant
- [ ] Le curseur est visible **sur les deux copies** — sinon on navigue à l'aveugle
      dans celle qu'on regarde
- [ ] Hors mode côte à côte, aucun changement mesurable (taille, position, DOM)
- [ ] Mesuré, pas jugé à l'œil : relever les positions des deux copies

## Ce qu'il ne faut pas rater

**Le curseur bouge** (`.gp-cursor` se déplace d'un élément à l'autre, et
`scrollIntoView` suit) : la copie doit être régénérée à chaque déplacement, sinon
elle affiche un curseur figé au mauvais endroit — pire que pas de copie du tout.

**Les deux fenêtres passent en `position: absolute` en plein écran**
(`.in-fullscreen`), parce qu'elles sont déplacées dans l'élément plein écran.
Vérifier les deux états.

Le mode côte à côte **force le plein écran** (`setVrMode`), donc c'est l'état
normal de ce ticket — mais le mode plat, lui, ne coupe pas l'image : la copie ne
doit apparaître qu'en `sbs`, pas dès que le VR est actif.
