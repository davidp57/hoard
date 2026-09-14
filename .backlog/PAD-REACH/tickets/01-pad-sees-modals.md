# BL-088 — Le pad doit voir les modals `div`

Status: ⬜ ready
Type: fix
Files: `frontend/index.html`

## Problem

`_gpOpenModal()` reconnaît `delete-dialog`, `move-dialog`, `export-dialog` et les
`dialog[open]`. Les autres overlays du projet sont des `div` : `tag-modal`,
`rename-overlay`, `mkdir-overlay`, `browse-modal`, `dest-picker-overlay`,
`dl-queue-modal`. Quand l'un d'eux est ouvert, la fonction renvoie `null`, le
dispatch tombe dans la branche browser et **le pad pilote la liste derrière le
modal** : le D-pad déplace un curseur invisible, A ouvre un fichier par-dessous.

Préalable au menu (BL-086), qui mène précisément à Renommer et Tags.

## What to build

- **Détection générique** : `_gpOpenModal()` rend le premier overlay réellement
  visible, quel que soit son nom — la liste en dur était déjà en retard de six
  entrées, une liste à tenir à jour rejouerait le même défaut.
- **Comportement minimum garanti dans tout modal non spécialisé** : `B` ferme,
  `D↑` / `D↓` déplacent le focus entre les contrôles, `A` active le contrôle
  focalisé. Aucun écran ne doit être un cul-de-sac au pad.
- Les handlers spécialisés existants (`delete`, `move`, `export`, `shortcuts`)
  gardent la priorité, leur comportement est inchangé.

## Acceptance criteria

- [ ] Ouvrir Tags, Renommer, Nouveau dossier, Browse, sélecteur de destination ou
      la file de téléchargements neutralise le curseur de la liste
- [ ] `B` ferme chacun de ces modals
- [ ] `D↑`/`D↓` + `A` permettent d'atteindre et d'activer leurs boutons
- [ ] Les quatre modals déjà spécialisés se comportent comme avant
