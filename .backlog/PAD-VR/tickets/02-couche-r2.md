# BL-128 — Couche VR sous R2

Status: ✅ done
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

La convergence ne se règle que par le menu Select, **qui recouvre la vidéo** : on
change la valeur sans voir l'effet, on referme, on regarde, on rouvre. Or c'est un
réglage qui ne se juge qu'à l'œil, et par petits pas.

`vrAdjustConvergence(deltaDeg)` (`index.html:5810`) existe depuis BL-122 et
**n'est appelée de nulle part** — du code mort. Seule `cycleVrConvergence()`, par
pas de 0,5° avec bouclage, est câblée, et seulement dans le menu.

Le **champ de vision** n'a pas davantage de raccourci manette : `vrZoom()` n'est
appelée que par la molette de la souris (`index.html:5961`), inutilisable sur un
Deck.

## What to build

Une **couche VR sous R2**, la dernière gâchette libre — L2 porte la bascule de
disposition depuis BL-125, L1 et R1 sont les modificateurs du lecteur.

| Geste (R2 maintenu) | Action |
|---|---|
| Stick droit | Regarder autour — déjà le cas sans R2, conservé pour la cohérence |
| **Stick gauche ↕** | **Zoom** (`vrZoom`) |
| **D-pad ←/→** | **Convergence** − / + (`vrAdjustConvergence`, enfin appelée) |
| **Clic stick gauche (L3)** | **Remettre le zoom** au défaut |
| **Clic stick droit (R3)** | **Remettre le regard** au centre |

Cadrage arrêté avec David le 2026-09-21.

- **Scinder `vrRecenter()`**, qui remet aujourd'hui le regard *et* le champ de
  vision d'un coup (`vr.yaw = 0; vr.pitch = 0; vr.fov = vrDefaultFov()`). Les deux
  gestes sont désormais distincts. Garder `vrRecenter()` pour **Maj+V** au clavier,
  qui fait bien les deux.
- **Le système de couches ne connaît que L1 et R1** : `_gpDispatch(btnIdx, l1, r1, gp)`
  et le traitement des sticks dans `_gpPoll` ignorent R2. Il faut l'y ajouter —
  c'est le vrai coût de ce ticket, pas les actions elles-mêmes.
- **Les sticks ne passent pas par le système de couches** du tout : ils sont
  traités à part dans `_gpPoll`. La condition R2 doit y être posée sans casser le
  seek (stick gauche X) ni le regard (stick droit).
- **Pas de pas trop gros** : 0,5° est le pas du menu, pensé pour un cycle. Pour un
  réglage à vue, viser plus fin et compter sur la répétition automatique du D-pad
  (`_gpNavRepeat` existe déjà) — mesurer ce qui est confortable plutôt que de le
  décréter.
- **L3 et R3 ont déjà un rôle sans modificateur** (couper le son, vitesse de
  lecture) : vérifier que la couche les intercepte bien et ne déclenche pas les
  deux.
- **Lister la couche dans la carte des boutons**, qui affiche déjà toutes les
  couches depuis BL-126. Une action que la carte ne montre pas est introuvable —
  la PR #49 l'avait déjà écrit à propos de L2 et R2.

## Acceptance criteria

- [ ] R2 maintenu, les cinq gestes du tableau font ce qu'ils annoncent
- [ ] L'effet est visible **pendant** le réglage, sans rien ouvrir
- [ ] Sans R2, tous les gestes gardent leur rôle actuel — seek, volume, regard,
      couper le son, vitesse
- [ ] La couche n'a d'effet qu'en mode VR ; ailleurs R2 ne fait rien
- [ ] La carte des boutons liste la couche
- [ ] Maj+V au clavier remet toujours regard **et** zoom

## Ce qu'il ne faut pas rater

**R2 est une gâchette analogique** : `buttons[7].pressed` bascule à un seuil, pas
au premier millimètre. Vérifier que le maintien est franc sur une vraie manette,
et pas seulement dans le code.

**Le mode côte à côte masquait les toasts — plus depuis BL-125**, qui les dessine
une fois par œil. Les toasts de `vrZoom` et `vrAdjustConvergence` sont donc
lisibles, et c'est ce qui donne la valeur chiffrée pendant qu'on règle à vue.
