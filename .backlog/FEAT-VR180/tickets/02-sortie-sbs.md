# BL-120 — Sortie côte à côte pour lunettes XR

Status: ✅ done
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

## Ce que le ticket n'avait pas vu

L'énoncé disait « le rapport d'image de chaque demi-écran vaut la moitié de celui
de la fenêtre ». **C'est faux dès que l'afficheur attend du *half-SBS***, ce qui
est le cas des lunettes XR et des téléviseurs 3D : chacune des deux moitiés y est
**réétirée sur toute la largeur**, donc l'image qu'un œil perçoit a le rapport du
canvas **entier**, pas celui du demi-tampon où elle est dessinée. Le calcul hérité
de BL-119 était celui du cas *full* et aurait donné, dans des lunettes, une image
fausse d'un facteur deux.

Comme rien ici ne permet de deviner ce que fait une paire de lunettes donnée, les
**deux dispositions sont livrées** (`half` par défaut), basculables à la touche
**B** et depuis le menu manette. Le mauvais réglage se voit en une seconde à
l'écran ; c'est donc une bascule qu'on tend à l'utilisateur, pas une valeur à
deviner.

Deux ajouts nés de l'usage, hors énoncé :

- **Les incrustations 2D sont masquées en `sbs`** (barre de commandes, toast,
  indicateur de volume, minuteur). Dessinées une fois sur une image qui va être
  coupée en deux, elles tombent à moitié dans chaque œil et ne sont lisibles
  nulle part. La manette et le clavier gardent la main.
- **Basculer `flat` ↔ `sbs` ne remet plus le regard à zéro.** C'est une
  comparaison qu'on fait en boucle, et perdre son cadrage à chaque bascule la
  rendait inutilisable. Le recentrage n'a plus lieu qu'en entrant depuis `off`.

## Mesures relevées

Mire équirectangulaire poussée dans le rendu livré, canvas 1200×675 (16:9).

**Disposition de sortie** — position de l'équateur à tangage 20°, qui doit tomber
à `y = −tan(φ) / tan(vfov/2)` :

| disposition | attendu | mesuré | écart |
|---|---|---|---|
| `half` | −0,6471 | **−0,6469** | 2·10⁻⁴ |
| `full` | −0,3235 | **−0,3234** | 1·10⁻⁴ |

Les deux diffèrent nettement (équateur ligne 555 contre 446) : la bascule a un
effet réel, et chacune tombe sur sa propre prédiction.

**Convergence** — colonne du méridien 0 dans chaque demi-vue :

| convergence | œil gauche | œil droit | écart |
|---|---|---|---|
| 0° | 299 | 299 | **0 px** |
| 6° | 284 | 315 | 31 px, symétrique |

**Incrustations et restitution** : en `sbs`, `#controls`, `#toast`, `#vol-osd` et
`#mini-time` sont tous à `display: none` ; en sortant du mode, tous reviennent et
le canvas est retiré. **Cadrage** : lacet 31°, tangage −12°, champ 77° survivent à
`flat → sbs` et à `sbs → flat`, et sont remis à zéro par `off → flat`.

## Acceptance criteria

- [x] En mode `sbs`, deux vues sont dessinées côte à côte, chacune depuis son œil
- [x] Les deux vues bougent ensemble quand on regarde autour (lacet, tangage et
      champ sont communs ; seule la convergence les sépare)
- [x] Aucune des deux vues n'est étirée — **mais pas pour la raison écrite dans
      l'énoncé** : c'est la disposition de sortie qui fixe le rapport, voir plus haut
- [x] La convergence à zéro laisse les deux vues rigoureusement alignées (même
      colonne, au pixel)
- [x] Le passage `flat` ↔ `sbs` ne coupe pas la lecture
- [ ] **Vérifié sur le Deck relié aux lunettes, en mode 3D des lunettes** — reste
      dû, et c'est la seule vérification que ce poste ne peut pas faire. C'est aussi
      elle qui dira laquelle des deux dispositions est la bonne.
