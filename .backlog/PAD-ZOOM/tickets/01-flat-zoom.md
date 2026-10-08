# BL-140 — Zoom et déplacement sous R2 sur une vidéo plate

Status: 🔄 in-progress

## Quoi

| R2 maintenu, vidéo plate | Effet |
|---|---|
| Stick gauche ↕ | zoom, 1× à 4×, multiplicatif (1× → 4× en ~1,4 s à fond) |
| Stick droit | déplacement, borné à l'image réellement affichée |
| L3 | retour à 1× |
| Autres boutons | rien, comme sous la couche VR |

- Sticks fixes sous R2, comme la couche VR : l'inversion des sticks n'a plus rien à échanger.
- Relâcher R2 laisse le zoom en place ; volume, vitesse et avance reviennent aux sticks.
- Remise à 1× : changement de fichier, fermeture du lecteur, changement de visionneuse, passage en VR (qui a son propre zoom).
- Le zoom garde le milieu de l'écran sur le même point de l'image.

## Mise en œuvre

- `transform: translate() scale()` sur la `<video>`, plus un `clip-path` recalculé dans le repère de l'élément pour que l'image agrandie ne déborde pas sur la barre de contrôle.
- Le mode côte à côte global recopie l'attribut `style` de la `<video>` sur le canvas qui la remplace : l'œil droit zoome sans code de plus.
- En mode « remplir » (`object-fit: cover`), le déplacement est borné à la boîte, pas à l'image rognée.

## Vérification

Manette simulée rendue à `navigator.getGamepads`, boucle de scrutation réelle, sur `small/clip.mp4` son coupé :

- 0,5 s à fond vers le haut → 1,65× (e^0,5) ; déplacement à droite borné à `(900 × 1,65 − 900) / 2` px ;
- mini-carte : cadre 60,7 % × 72,7 %, collé au bord droit après le déplacement ;
- A sous R2 ne relance pas la lecture ; R2 relâché, le stick gauche règle le volume et le zoom reste ;
- L3 sous R2 → 1×, `transform` et `clip-path` retirés, toast « ⛶ zoom 1× » ;
- passage en VR → zoom plat remis à 1× ;
- côte à côte global : le canvas de la copie porte le même `transform` et le même `clip-path`, les deux yeux zoomés à l'identique sur la capture.

Reste : l'essai sur le Frame.
