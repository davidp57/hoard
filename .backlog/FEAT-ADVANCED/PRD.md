# Lot FEAT-ADVANCED — Fonctionnalités avancées (reste : thème clair + multi-utilisateur)

Status: ⬜ ready
Branch: feature/light-theme (BL-013) · feature/multi-user (BL-015) → PR → develop

## Problem Statement

Hoard couvre désormais le gros de ses fonctionnalités produit (tri, marquage vu,
renommage, sous-titres, plein écran fenêtré — tous livrés). Deux besoins avancés
restent ouverts :

1. **Thème clair** — l'UI est exclusivement sombre. Certains environnements (forte
   luminosité, préférence personnelle) sont plus confortables en thème clair.
2. **Progression multi-utilisateur** — la table `progress` stocke une seule ligne
   d'avancement par fichier. Dès que plusieurs personnes utilisent la même instance
   Hoard, leurs progressions se mélangent.

## Solution

- **Thème clair** : toggle persisté localement, basé sur les tokens de couleur déjà
  centralisés dans `:root`. Aucun backend nécessaire.
- **Multi-utilisateur** : séparer la progression par utilisateur tout en préservant
  l'architecture légère (SQLite natif, pas d'ORM). Présuppose la couche
  d'authentification (HTTP Basic, BL-011, livrée dans `SECURITY-QUALITY-UX`).

## User Stories

1. En tant qu'utilisateur sur un écran très lumineux, je veux basculer en thème
   clair, pour lire la liste et l'UI confortablement.
2. En tant que foyer partageant une instance Hoard, nous voulons chacun notre
   progression de lecture, pour ne pas écraser celle des autres.

## Implementation Decisions

- Thème clair : variables CSS dans `:root` uniquement, bascule via `localStorage`
  (cohérent avec l'usage actuel de `localStorage` limité aux préférences device-local).
- Multi-utilisateur : clé utilisateur dérivée de l'auth Basic ; lignes `progress`
  étendues par utilisateur. Garder l'absence d'auth fonctionnelle (mono-utilisateur
  par défaut, aucune régression).

## Testing Decisions

- Multi-utilisateur : tests d'isolation des lignes `progress` par utilisateur,
  + non-régression du mode mono-utilisateur (auth désactivée).
- Thème clair : pas de harness frontend (single-file) → validation visuelle +
  `node --check`.

## Out of Scope

- Comptes utilisateurs complets / gestion de rôles (l'auth reste HTTP Basic).
- Settings par utilisateur autres que la progression.

## Further Notes

- BL-015 dépendait de BL-011 (auth) — désormais livré, donc plus de blocage.
- Lockstep doc : `docs/user-guide.*` + `docs/changelog-user.fr.md` + `CHANGELOG.md`.

## Déjà livré dans ce lot

Tickets de ce lot terminés et conservés ici pour le contexte (détail dans
`CHANGELOG.md` et l'historique git) :

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-002 | Tri liste : taille + état de lecture | feat | ✅ done |
| BL-003 | Marquer manuellement vu / non vu | feat | ✅ done |
| BL-006 | Renommage de fichiers/dossiers depuis l'UI | feat | ✅ done |
| BL-008 | Sous-titres (`.srt` / `.ass` sidecar) | feat | ✅ done |
| BL-066 | Plein écran fenêtré immersif par défaut (desktop) | feat | ✅ done |
