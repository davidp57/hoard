# BL-120 — Sortie côte à côte pour lunettes XR

Status: ⬜ ready
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

BL-119 rend une vue plate d'un seul œil. Sur un Steam Deck relié à des lunettes XR
(Viture Beast), l'affichage est **stéréo** : les lunettes attendent une image dont la
moitié gauche va à l'œil gauche et la moitié droite à l'œil droit, et font
elles-mêmes la séparation. Il manque donc une sortie qui dessine les deux vues.

## Dependencies

BL-119 (socle de rendu et pilotage du regard).

## What to build

- Un mode de sortie `sbs` à côté du mode `flat`, sur le même programme WebGL : deux
  passes de dessin, `gl.viewport()` sur la moitié gauche puis sur la moitié droite,
  chacune avec les bornes UV de son œil.
- Le lacet, le tangage et le champ de vision sont **communs aux deux yeux** : chaque
  œil possède déjà son hémisphère, il n'y a pas de parallaxe à recalculer.
- Un décalage de convergence en option (un petit écart de lacet entre les deux yeux),
  à zéro par défaut. Valeur en dur ici, exposée par BL-122.
- Le rapport d'image de chaque demi-écran vaut la moitié de celui de la fenêtre :
  le champ de vision vertical se calcule à partir de là, sinon l'image est étirée.
- Bascule entre `flat` et `sbs` depuis la barre du lecteur et au clavier ; le mode
  retenu est mémorisé par BL-121.
- Plein écran : le mode `sbs` n'a de sens qu'en plein écran sur l'écran des lunettes.
  Entrer en `sbs` propose le plein écran.

## Acceptance criteria

- [ ] En mode `sbs`, deux vues sont dessinées côte à côte, chacune depuis son œil
- [ ] Les deux vues bougent ensemble quand on regarde autour
- [ ] Aucune des deux vues n'est étirée : le champ de vision tient compte du rapport
      d'image de la demi-fenêtre
- [ ] La convergence à zéro laisse les deux vues rigoureusement alignées
- [ ] Le passage `flat` ↔ `sbs` ne coupe pas la lecture
- [ ] Vérifié sur le Deck relié aux lunettes, en mode 3D des lunettes
