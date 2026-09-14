# BL-089 — Menu contextuel dans le lecteur

Status: ✅ done
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

Après BL-086, le lecteur restait le seul endroit où **Select** voulait dire autre
chose (ouvrir les Paramètres), et **⏱ Départ dossier** était le dernier bouton de
l'interface sans chemin manette.

Relevé des boutons disponibles dans le lecteur : **L2 et R2 (index 6 et 7) ne sont
utilisés nulle part** — aucune couche, aucun contexte, aucune lecture de
`buttons[6]` ou `buttons[7]` dans le code. Tout le reste est pris dans les quatre
couches. Mais **la carte des boutons ne dessine ni L2 ni R2** (le SVG n'étiquette
que 0-5, 8, 9 et 12-15) : y mapper une action l'aurait rendue introuvable, et
l'ajouter au schéma tracé à la main était le vrai coût de cette voie.

## Implementation Decisions

- **Le menu plutôt qu'un combo.** Découvrable par construction, aucune carte à
  redessiner, et la règle devient uniforme : *Select ouvre le menu, partout*.
  L2 et R2 restent en réserve pour une action de lecture fréquente — c'est ce à quoi
  deux gâchettes servent mieux qu'à un réglage posé une fois par dossier.
- **Le menu du lecteur n'est pas un doublon de la barre de contrôle.** Le lecteur est
  déjà entièrement mappé : le menu porte ce qui n'a pas de bouton (le départ du
  dossier), les cycles rarement utilisés, les actions sur le fichier, et les entrées
  système.
- **Les overlays suivent le plein écran.** Le déplacement vers l'élément plein écran
  ne nommait que trois dialogues ; le menu pouvant désormais ouvrir n'importe lequel
  depuis le plein écran, tous les `.gp-modal` suivent — sauf l'écran de code PIN,
  dont le flux quitte le plein écran de lui-même.

## What was built

- `8: 'open_menu'` dans `player_base`, donc Select ouvre le menu aussi dans le lecteur.
- `_gpMenuBuildPlayer()` : départ du dossier, marquer vu/non vu, sous-titres,
  Fit/Fill, vitesse, export des segments (si des segments existent), renommer, tags,
  déplacer, supprimer, fermer le lecteur, Paramètres, Aide manette.
- La liste des overlays déplacés en plein écran est généralisée.

## Acceptance criteria

- [x] Select ouvre le menu dans le lecteur, et n'ouvre plus les Paramètres
- [x] ⏱ Départ dossier est applicable à la manette, et écrit bien l'override du dossier
- [x] La carte des boutons annonce « Menu contextuel » sur Select, onglet Joueur
- [x] Le menu du navigateur de fichiers est inchangé
- [ ] Les fenêtres restent visibles en plein écran natif — **non vérifié** : le
      plein écran natif n'a pas pu être déclenché dans le navigateur de preview.
      Le code généralise un mécanisme existant qui fonctionnait pour trois
      dialogues, et le retour dans `<body>` est confirmé.
