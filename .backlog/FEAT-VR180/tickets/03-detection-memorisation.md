# BL-121 — Détection des fichiers VR et mémorisation du mode

Status: ⬜ ready
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`,
`docs/user-guide.*.md`, `docs/developer.en.md`

## Problem

BL-119 et BL-120 rendent le mode VR atteignable, mais seulement à la main. Or aucun
fichier de la médiathèque ne porte de métadonnée sphérique (`st3d` / `sv3d` absents
des 24 fichiers relevés) : rien ne dira au lecteur qu'il ouvre un fichier VR, et le
choix serait à refaire à chaque ouverture, sur chaque machine.

## Dependencies

BL-119.

## What to build

### Détection (backend)

- Un helper `_guess_vr_layout(name, width, height)` qui rend la disposition devinée
  (`sbs180` ou `None`) à partir de deux indices :
  - **ratio d'image 2:1** — l'œil est alors carré, cas de 23 des 24 fichiers relevés ;
  - **motifs de nom** : `_LR`, `3dh`, `180x180`, `vr180`, `sbs`, `oculusrift`, `180_`.
  Un ratio 2:1 suffit ; un 16:9 doit être confirmé par un motif de nom (c'est le cas
  du fichier anamorphosé 3840×2160).
- Le champ `vr` exposé par `/api/files` et `/api/search` : la disposition devinée, ou
  celle que l'utilisateur a fixée si elle existe.

### Mémorisation (backend)

- Le mode retenu est stocké **côté serveur**, par fichier, pas dans `localStorage` :
  il doit suivre d'une machine à l'autre, comme la progression.
- `POST /api/vr-mode` : chemin + mode (`off`, `flat`, `sbs`), validé par `safe_path()`.
- Le choix explicite prime toujours sur la devinette, y compris pour dire « ce
  fichier n'est pas de la VR » quand la détection se trompe.

### Frontend

- Un marqueur discret sur les entrées reconnues comme VR dans la liste de fichiers.
- Ouverture d'un fichier VR : le mode mémorisé s'applique ; à défaut, la disposition
  devinée arme le mode sans l'activer — l'activation reste un geste, pour ne pas
  imposer le rendu VR à quelqu'un qui voulait juste vérifier un fichier.
- La bascule de mode écrit le choix via `POST /api/vr-mode`.

### Garde-fou

- Le mode VR est refusé sur le flux `/api/transcode`. Un fichier VR passe par
  `/api/file` ou ne passe pas : transcoder du 8K60 mettrait le NAS à genoux.

## Acceptance criteria

- [ ] Les 24 fichiers de l'échantillon sont reconnus (ratio, ou nom pour le 16:9)
- [ ] Un fichier 2:1 qui n'est pas de la VR peut être marqué `off`, et le reste
- [ ] Le mode choisi sur une machine s'applique sur l'autre
- [ ] `safe_path()` est appliqué sur le chemin reçu, et un chemin hors racine est
      rejeté (test)
- [ ] Le champ `vr` apparaît dans `/api/files` et `/api/search`
- [ ] Le mode VR n'est pas proposé sur un flux transcodé
- [ ] Une vidéo ordinaire n'est jamais reconnue comme VR
