# Lot SORT-WATCHED — Trier par date de dernier visionnage

Status: 🔄 in-progress
Branch: feature/sort-last-watched → PR → develop

## Problem Statement

La barre de tri propose un critère **Date**, qui trie sur le `st_mtime` du système
de fichiers. Ce n'est pas une date d'accès : lire une vidéo n'écrit rien sur le
disque, et le `mtime` d'un dossier ne bouge que sur ajout / suppression / renommage
d'un enfant **direct** — il ne remonte jamais depuis la profondeur.

Conséquence observée : après avoir regardé
`[[BackRoomCastingCouch/[…][PACK].SiteRip…/brcc1740-1080p.mp4`, le dossier
`[[BackRoomCastingCouch` reste en 14ᵉ position de la liste. Il devrait être en tête,
c'est celui qui contient la dernière vidéo consultée.

Aucun tri par date de visionnage n'existait dans Hoard, alors que la donnée est en
base depuis toujours : `progress.updated_at` est rafraîchie à chaque sauvegarde de
position, et n'était jamais lue.

## Solution

Un **cinquième critère de tri « Vu »**, alimenté par un nouveau champ `last_watched`
sur chaque entrée de `/api/files` et `/api/search`. Un dossier hérite de la date du
média le plus récemment regardé **n'importe où en dessous de lui**, à n'importe
quelle profondeur.

## User Stories

1. En tant qu'utilisateur, je veux retrouver en tête de liste le dossier dont j'ai
   regardé une vidéo en dernier, même si elle est enfouie dans des sous-dossiers,
   pour reprendre là où j'en étais sans me souvenir du chemin.
2. En tant qu'utilisateur, je veux garder le tri par date fichier, qui répond à une
   autre question : « qu'est-ce qui vient d'arriver dans ce dossier ».

## Implementation Decisions

- **Un critère de plus, pas une redéfinition de « Date »**. Le tri par `mtime` a sa
  propre valeur — il fait remonter les téléchargements récents. Le remplacer aurait
  corrigé une question en cassant l'autre.
- **Index construit en une passe, sans I/O**. `_last_watched_index()` lit la table
  `progress`, et pour chaque ligne remonte sa chaîne d'ancêtres en gardant le
  maximum. Coût `O(lignes × profondeur)`, aucun `stat`, aucun `rglob` — contrairement
  à `get_folder_state()`, qui est justement exclu de la recherche pour cette raison.
  L'index sert donc aussi `/api/search`, où le tri reste cohérent.
- **`strftime('%s', updated_at)` côté SQLite** : la colonne est un `TIMESTAMP` texte
  UTC. Le frontend reçoit un entier epoch, directement comparable comme `mtime`.
- **Les jamais-vus (`last_watched = 0`) sont groupés en fin de liste**, quel que soit
  le sens du tri, et départagés entre eux par date fichier. Les intercaler aurait
  produit un bloc d'entrées à 0 dans un ordre arbitraire — inversé, il aurait mis
  les non-vus en tête alors que le critère demandé porte sur ce qui a été vu.
- **Les galeries fonctionnent sans cas particulier** : une galerie porte sa propre
  ligne de progression sur le chemin du dossier, qui entre dans l'index comme un
  fichier.

## Testing Decisions

- Le cas qui justifie le lot : un média **à deux niveaux de profondeur** doit faire
  remonter sa date jusqu'au dossier de tête, avec la même valeur au niveau
  intermédiaire.
- Un dossier voisin non regardé doit rester à `0` — sans quoi l'index déborderait.
- La recherche expose le champ, puisqu'elle partage le tri côté client.

## Out of Scope

- Une date de dernier **accès** au sens filesystem (`st_atime`) : elle change à
  chaque parcours récursif de Hoard lui-même, elle ne veut rien dire ici.
- Un historique de visionnage avec plusieurs dates par fichier : une seule date, la
  dernière, suffit au besoin.

## Tickets

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-085 | Tri « Vu » par date de dernier visionnage | feat | 🔄 |
