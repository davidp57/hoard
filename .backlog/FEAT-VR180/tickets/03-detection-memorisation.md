# BL-121 — Détection des fichiers VR et mémorisation du mode

Status: ✅ done
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

## Écart assumé par rapport à l'énoncé

L'énoncé plaçait **toute** la détection côté serveur, ratio d'image compris. Ce
n'est pas tenable : `/api/files` ne connaît pas les dimensions en pixels, et les
obtenir voudrait dire **un `ffprobe` par entrée à chaque ouverture de dossier**,
sur un NAS choisi faible. Livré : le **nom** est lu côté serveur (gratuit, il est
déjà là), le **ratio 2:1** est vérifié dans le lecteur, où l'élément `<video>`
donne ses dimensions pour rien, au moment précis où la réponse sert.

Ce découpage n'affaiblit rien : la liste affiche le marqueur pour tout ce que le
nom trahit, et le reste se révèle à l'ouverture — c'est-à-dire avant qu'on en ait
besoin.

## Mesures relevées

Détection par nom, sur les 23 fichiers distincts de l'échantillon et sur une
série de noms ordinaires :

| | |
|---|---|
| reconnus par le nom | **15 / 23** |
| reconnus par le ratio (dans le lecteur) | les **8** restants |
| faux positifs sur des noms ordinaires | **0** |

Un motif `180` isolé figurait dans la première version. Il marquait
« Episode 180 - The Long Goodbye.mkv », et mesuré contre l'échantillon il ne
reconnaissait **aucun** fichier que les autres motifs n'attrapaient déjà : il
coûtait un faux positif et ne rapportait rien. Retiré.

Chaîne complète vérifiée dans le navigateur : `vr_hint` sur le fichier VR et
`null` sur un clip ordinaire, un seul marqueur rendu dans la liste, le mode armé
sans être activé à l'ouverture, le choix écrit par `POST /api/vr-mode`, puis
**réappliqué seul après un rechargement complet de la page**.

## Acceptance criteria

- [x] Les fichiers de l'échantillon sont reconnus — 15 par le nom, 8 par le ratio
- [x] Un fichier 2:1 qui n'est pas de la VR peut être marqué `off`, et le reste
- [x] Le mode choisi sur une machine s'applique sur l'autre (mémorisé côté serveur,
      réappliqué après rechargement complet)
- [x] `safe_path()` est appliqué sur le chemin reçu, et un chemin hors racine est
      rejeté (test)
- [x] Les champs `vr_hint` et `vr_mode` apparaissent dans `/api/files` et `/api/search`
- [x] Le mode VR n'est pas proposé sur un flux transcodé
- [x] Une vidéo ordinaire n'est jamais reconnue comme VR (0 faux positif mesuré)
- [x] **Ajouté au périmètre** : la ligne suit un renommage et disparaît avec le
      fichier — sans quoi un nouveau fichier au même chemin héritait du mode d'un
      inconnu. Les deux cas sont testés.
