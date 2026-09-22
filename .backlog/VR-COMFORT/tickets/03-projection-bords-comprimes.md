# BL-135 — Voir plus large sans perdre le relief au centre

Status: ✅ done
Type: feat
Files: `frontend/index.html` (shader VR), `docs/user-guide.*.md`
Fait le 2026-09-22, David ayant tranché avant l'essai : « fais VR-COMFORT avec un setting numérique (désactivé, puis divers degrés de compression) ».

## Problem

Au champ juste (45°), la profondeur est bonne et **on voit peu de la scène**.
David : « c'est très zoomé, on ne voit très peu de la scène ; tu crois qu'on
pourrait jouer avec la géométrie pour dézoomer la scène tout en gardant un fov
à 45° ? »

Pas avec la projection actuelle : sur un écran plat d'angle fixe, la largeur de
scène et l'échelle de profondeur sont **le même bouton**. Élargir rapetisse tous
les angles, donc l'écart entre les deux images, donc la profondeur.

## What to build

Une projection **non rectilinéaire** : le centre reste à l'échelle juste — la
profondeur y est correcte, c'est là qu'on regarde — et la compression augmente
progressivement vers les bords pour y faire rentrer plus de scène. Une dizaine
de lignes dans le shader existant, plus un dosage réglable.

- **Un basculement dans le menu Select**, demandé explicitement : ça se juge en
  regardant, donc ça doit s'essayer sans ouvrir les réglages.
- Le dosage est un réglage, le basculement est un geste.

## Acceptance criteria

- [x] Au centre, la profondeur est celle qu'on a au champ juste sans compression — échelle centrale inchangée à 10⁻⁶ près à toutes les doses
- [x] On voit sensiblement plus de scène à dosage non nul — une case de mire de plus de chaque côté à 40 %, deux à 100 %
- [x] Le basculement est dans le menu **Select**, et cycle 0 → 20 → … → 100 → 0
- [x] Aucun décalage **vertical** introduit entre les deux yeux — l'élargissement ne touche qu'à l'azimut, l'élévation sort inchangée de la projection d'origine
- [x] Mesuré sur une mire quadrillée ; **défaut à 0**, parce que c'est un échange et non une amélioration. Le dosage qui convient à l'usage reste à trouver en regardant de vrais films — c'est là que le réglage prend son sens.

## Ce qu'il ne faut pas rater

**Comprimer uniquement en horizontal.** La hauteur doit rester fonction de la
seule élévation. Une compression **radiale** décalerait les deux yeux
verticalement l'un par rapport à l'autre pour tout point hors axe — et le
décalage vertical est le plus fatigant de tous, celui qu'aucun réglage ne
rattrape : la convergence ne joue que sur l'horizontale.

**La profondeur s'aplatit là où ça comprime.** Les deux yeux subissent le même
gauchissement, donc l'écart entre eux est multiplié par la pente locale : 1 au
centre, moins vers les bords. C'est le prix, et il se paie en périphérie, où
l'œil est le moins exigeant. À dire dans la doc plutôt qu'à cacher.

**Les lignes droites s'incurvent aux bords.** Acceptable sur une scène filmée,
beaucoup moins sur de l'architecture. Raison de plus pour que ce soit un
basculement et pas un état permanent.

## Ce qui a été fait, et pourquoi là

L'élargissement est appliqué **dans l'espace de la vue, avant toute rotation**.
C'est le seul endroit qui marche, et trois propriétés en découlent :

- le point fixe est le milieu de **ce qu'on regarde**, pas l'axe avant de la
  source — sinon la propriété serait perdue dès qu'on tourne la tête ;
- l'**élévation** sort inchangée de la projection d'origine, donc aucun décalage
  vertical n'est ajouté entre les deux yeux ;
- la **convergence**, appliquée après, reste un décalage uniforme au lieu d'être
  étirée inégalement sur l'écran.

Le coefficient du shader est dérivé du champ de vision côté JS plutôt qu'exposé
brut : le réglage garde ainsi le même sens quand le champ change.
