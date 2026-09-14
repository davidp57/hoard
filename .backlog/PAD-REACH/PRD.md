# Lot PAD-REACH — Toute l'UI atteignable à la manette

Status: ✅ done
Branch: feature/pad-reach → PR → develop

## Problem Statement

Le player est presque intégralement pilotable à la manette. Le **browser** ne l'est
quasiment pas. Relevé sur le dispatch (`_gpDispatch`), contexte « aucun média
ouvert » :

- **Atteignable** : curseur (D-pad), ouvrir (A), remonter (B), réglages (Start
  *et* Select, doublon), supprimer et déplacer l'entrée au curseur (L1+R1+B / +X).
- **Hors d'atteinte** : les 5 critères de tri et le sens · renommer · tags ·
  filtre par tag · épingler · nouveau dossier · rafraîchir · recherche · accueil ·
  Browse… · file de téléchargements · et l'overlay d'aide manette lui-même, Start
  étant détourné vers les réglages dans ce contexte.

Le tri n'est d'ailleurs accessible **ni au pad ni au clavier** : `setSortBy` et
`toggleSortDir` n'ont que des `onclick`.

Deux défauts se sont ajoutés à l'audit :

- **Quatre boutons mappés sur des actions inertes.** Dans le browser, X, Y, L3 et
  R3 pointent sur `toggle_watched`, `fullscreen`, `mute` et `speed_cycle`, qui
  testent tous `hasVideo` en premier et ne font donc rien. Un bouton qui ne répond
  pas se lit comme une panne.
- **Six modals où le pad passe à travers.** `_gpOpenModal()` ne reconnaît que
  `delete`, `move`, `export` et les vrais `<dialog>`. `tag-modal`,
  `rename-overlay`, `mkdir-overlay`, `browse-modal`, `dest-picker-overlay` et
  `dl-queue-modal` sont des `div` : quand l'un est ouvert, le pad **continue de
  piloter la liste derrière** — le D-pad déplace un curseur invisible et A ouvre un
  fichier sous le modal.

## Solution

Un **menu contextuel** ouvert par **Select**, qui expose ce qui s'applique à
l'endroit où l'utilisateur se trouve, plus la remise en état du dispatch et des
modals sans lesquels ce menu mènerait à des impasses.

## User Stories

1. En tant qu'utilisateur à la manette, je veux changer le tri de la liste sans
   poser le pad pour attraper l'écran tactile.
2. En tant qu'utilisateur à la manette, je veux renommer, tagger ou épingler une
   entrée depuis la liste.
3. En tant qu'utilisateur, je veux marquer un fichier vu ou non vu sans l'ouvrir.
4. En tant qu'utilisateur à la manette, je ne veux jamais me retrouver devant un
   écran dont je ne peux pas sortir au pad.

## Implementation Decisions

- **Select, pas LB/RB.** LB et RB ne déclenchent jamais d'action : la boucle de
  détection les saute explicitement (`if (i === 4 || i === 5) continue`), ce sont
  des modificateurs purs. Leur donner une action demanderait de la déclencher au
  **relâchement**, sous condition qu'aucun autre bouton n'ait été pressé — un délai
  perçu et une règle de plus. Select, lui, fait aujourd'hui exactement la même chose
  que Start dans le browser : il est libre, sans ambiguïté et sans latence.
- **Menu contextuel, pas menu unique.** Deux sections distinctes selon la position :
  actions de liste, et actions sur l'entrée au curseur. Afficher un menu complet en
  grisant la moitié des lignes obligerait l'utilisateur à apprendre ce qui ne marche
  pas ; n'afficher que ce qui s'applique se lit sans rien apprendre.
- **« Vu » devient un état explicite** (colonne `watched` dans `progress`, migration
  `ALTER TABLE`), prioritaire sur le pourcentage de position. Marquer vu un fichier
  jamais ouvert n'a pas de durée à sa disposition : les deux alternatives étaient
  d'aller la sonder à `ffprobe` à chaque marquage, ou d'écrire une position
  inventée qui affiche « 0:01 / 0:01 » sous le nom et saute à la première lecture.
  « Vu » est un état, pas une position — c'est la table qui devait le dire.
- **Les actions inertes sont retirées du fallback browser** plutôt que laissées en
  place : `fullscreen`, `mute` et `speed_cycle` n'ont pas de sens hors lecture.
  `toggle_watched` sur X, lui, en a un — il est réparé pour agir sur le curseur,
  ce qui livre BL-003 au passage.
- **Modals reconnus par leur état visible**, pas par une liste de noms à tenir à
  jour : l'audit a montré que la liste en dur était déjà en retard de six entrées.

## Testing Decisions

- Le backend est testé sur la nouvelle colonne : marquer vu un fichier **sans
  aucune ligne de progression**, marquer non vu, et la priorité de `watched` sur le
  pourcentage dans `get_progress` et `get_folder_state`.
- La migration est testée sur une base créée sans la colonne.
- Le frontend n'a pas de banc de test dans ce projet : le menu et le dispatch sont
  vérifiés à la manette et à la souris dans l'app lancée.

## Out of Scope

- Le remappage utilisateur du menu (il reste sur Select, non reconfigurable).
- Un menu contextuel dans le player : le player est déjà couvert, à l'exception de
  ⏱ *Départ dossier*, ajouté au menu côté liste si le contexte s'y prête.
- La recherche au pad par clavier virtuel : le champ est exposé dans le menu, la
  saisie reste au clavier physique ou tactile.

## Tickets

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-088 | Le pad doit voir les modals `div` | fix | ✅ done |
| BL-087 | Retirer les actions inertes du dispatch browser | fix | ✅ done |
| BL-003 | Marquer vu / non vu depuis la liste | feat | ✅ done |
| BL-086 | Menu contextuel manette (Select) | feat | ✅ done |
