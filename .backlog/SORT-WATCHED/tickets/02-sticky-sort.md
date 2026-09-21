# BL-118 — Le tri choisi dans la barre est mémorisé

Status: ✅ done
Type: fix
Files: `frontend/index.html`, `tests/test_api.py`, `docs/user-guide.*.md`

## Problem

Le tri choisi dans la barre ne vivait qu'en mémoire de page. `sortBy` / `sortDir`
sont initialisées depuis `cfg.sort_by` / `cfg.sort_dir` au démarrage et n'étaient
jamais réécrites : passer la liste en « Vu », recharger la page (ou revenir depuis
l'iPad) ramenait le tri « Date ». Pire, ouvrir **Paramètres** et enregistrer
réappliquait la valeur du `<select>`, donc annulait le tri courant sans qu'on l'ait
touché.

Le réglage `sort_by` / `sort_dir` existe en base depuis toujours et le `POST
/api/settings` accepte déjà un corps partiel (les champs absents sont laissés
inchangés) : rien à ajouter côté backend.

## What to build

- `persistSort()` appelée par `setSortBy()` et `toggleSortDir()` : met à jour
  `cfg.sort_by` / `cfg.sort_dir` puis `POST /api/settings` avec ces deux champs
  seuls. Écriture regroupée par un `setTimeout` de 400 ms — la barre est une rangée
  de boutons qu'on essaie avant de se fixer, et chaque `POST` inscrit une ligne dans
  le journal d'audit consultable depuis l'UI.
- `fetch` brut et non `apiFetch` : ce dernier affiche un toast « erreur réseau », ce
  qui n'a pas de sens pour une écriture de confort en arrière-plan alors que le tri,
  lui, s'est bien appliqué à l'écran. `keepalive: true` + un `pagehide` qui vide le
  minuteur en attente, sans quoi fermer l'onglet dans les 400 ms perdrait le choix.
- Mise à jour de `cfg` **avant** l'écriture réseau : c'est `cfg.sort_by` que lit
  `openSettings()` pour remplir le `<select>`, donc un enregistrement des
  paramètres ne peut plus écraser le tri courant.
- Réglage renommé « Tri par défaut » → « **Tri de la liste** », avec la mention
  qu'il reflète le tri choisi dans la barre. « Par défaut » était devenu faux.

## Acceptance criteria

- [x] Choisir « Vu », recharger la page : la liste est toujours triée par « Vu »
- [x] Le sens du tri (↑ / ↓) est mémorisé de la même façon
- [x] Ouvrir les paramètres et enregistrer ne remet pas le tri sur sa valeur d'avant
- [x] Le `POST` partiel ne touche aucun autre réglage (test API)
- [x] Le tri suit d'un appareil à l'autre (réglage serveur, pas `localStorage`)
