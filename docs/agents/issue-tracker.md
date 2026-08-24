# Issue tracker : dossier local `.backlog/`

Les lots, PRD et tickets de ce repo vivent en markdown sous `.backlog/`.
Langue des artefacts : **français** (comme le backlog, le CHANGELOG et les release notes).

## Conventions

- Un lot par dossier : `.backlog/<LOT-ID>/` (LOT-ID sémantique en MAJUSCULES, ex.
  `FEAT-ADVANCED`, `ARCH-PERF`).
- Le PRD est `.backlog/<LOT-ID>/PRD.md` (template Matt Pocock ; pas de `## Goal` séparé).
- Les tickets sont `.backlog/<LOT-ID>/tickets/<NN>-<slug>.md`, numérotés à partir de
  `01` en ordre de dépendance (blockers d'abord).
- **IDs de tickets** : on conserve le schéma historique global `BL-NNN` dans le titre
  du ticket (`# BL-013 — …`), car il est référencé dans les commits, `CHANGELOG.md`,
  `ROADMAP.md` et les docs. Le préfixe `NN` du fichier n'est que l'ordre de dépendance.
- Le `Status:` est une ligne en tête de chaque PRD/ticket (voir `triage-labels.md`).
- L'index des lots (table de TOUS les lots + statut) est `.backlog/README.md`,
  maintenu **à la main** par l'agent (pas de script générateur).
- **Pas d'estimations** : ni temps, ni table de calibration, ni colonne `Est.`/`Prio`
  dans les artefacts (décision projet).
- Les lots terminés sont déplacés vers `.backlog/archive/<LOT-ID>.md` (compact, table
  de tickets préservée) une fois clos depuis plus de 3 jours.

## Quand un skill dit « publier dans l'issue tracker »

- Un PRD → écrire `.backlog/<LOT-ID>/PRD.md`, créer le dossier si besoin, et ajouter
  une ligne à `.backlog/README.md`.
- Un ticket/issue → écrire `.backlog/<LOT-ID>/tickets/<NN>-<slug>.md`.
- Les nouveaux artefacts sont créés à `Status: ⬜ ready`.

## Quand un skill dit « récupérer le ticket pertinent »

Lire le fichier au chemin référencé. L'utilisateur passe normalement l'ID de lot ou
le chemin de ticket directement.

## Lien avec ROADMAP

`ROADMAP.md` reste la source de vérité du **séquencement** (versions, ordre de
livraison). `.backlog/` est la source de vérité du **scope + statut**.
