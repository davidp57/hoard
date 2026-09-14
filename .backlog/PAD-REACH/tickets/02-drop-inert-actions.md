# BL-087 — Retirer les actions inertes du dispatch browser

Status: ✅ done
Type: fix
Files: `frontend/index.html`

## Problem

Dans le browser, le dispatch retombe sur `GP_DEFAULT_MAPPING.base` pour les boutons
non couverts par `browserMap`. X, Y, L3 et R3 y pointent sur `toggle_watched`,
`fullscreen`, `mute` et `speed_cycle` — qui testent tous `hasVideo` en premier et
ne font donc **rien**. Même chose pour L1+R1+A (`jump_0`), +Y (`open_export`) et
+D↓ (`jump_100`), la couche `lr` n'étant pas conditionnée à la présence d'un média.

Un bouton qui ne répond pas ne se distingue pas d'une manette en panne.

## What to build

- Le fallback browser ne retient que des actions qui ont un sens hors lecture.
  `fullscreen`, `mute`, `speed_cycle` et les `jump_*` en sortent.
- La couche `lr` est conditionnée au contexte, comme `l1` et `r1` : seuls
  `delete_current` et `move_current`, qui savent viser le curseur, restent actifs
  dans le browser.
- **Start rend l'overlay d'aide manette** : `browserMap` le détourne aujourd'hui
  vers les réglages, déjà couverts par Select. Après ce lot Select ouvre le menu,
  donc Start reprend `open_overlay` comme dans le player, et les réglages restent
  atteignables depuis le menu.
- `toggle_watched` n'est pas retiré mais réparé — voir BL-003.

## Acceptance criteria

- [x] Aucun bouton du browser ne déclenche une action sans effet
- [x] Start ouvre l'aide manette dans le browser comme dans le player
- [x] Les réglages restent atteignables au pad
- [x] Le comportement du player est inchangé
