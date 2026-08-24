---
status: accepted
date: 2026-06-27
---

# Restructuration du backlog en dossiers `.backlog/` par lot

Le backlog vivait dans un `docs/backlog.md` monolithique (~33 KB) + un
`docs/backlog-archive.md`. Avec la règle « une branche / une PR par lot », le
monolithe était une surface récurrente de conflits de merge et coûtait du contexte
agent à charger. On voulait aussi piloter le backlog avec les skills d'ingénierie
Matt Pocock (`to-prd`, `to-issues`, `triage`), qui sont agnostiques du tracker et se
configurent par repo (sans fork).

## Décision

Adopter une structure `.backlog/` par lot :

- **Lots actifs** = dossiers — `.backlog/<LOT-ID>/PRD.md` plus un
  `tickets/<NN>-<slug>.md` par ticket. LOT-ID sémantiques en MAJUSCULES
  (ex. `FEAT-ADVANCED`, `ARCH-PERF`).
- **Lots terminés** = fichiers compacts `.backlog/archive/<LOT-ID>.md` (table de
  tickets préservée, non splittée).
- Un seul vocabulaire `Status:` (⬜ ready · 🔄 in-progress · 🧑 waiting-human ·
  ✅ done · 🚫 wontfix) mappé sur les rôles de triage de Matt.
- Les IDs de tickets historiques `BL-NNN` sont **conservés** (référencés dans commits,
  CHANGELOG, ROADMAP, docs).
- **Abandon des estimations** (temps, table de calibration, colonnes `Est.`/`Prio`) :
  elles n'apportaient pas de valeur de pilotage et alourdissaient le backlog.
- Les skills Matt Pocock restent installés globalement et non modifiés ; la config
  par repo vit dans `docs/agents/*` + un bloc `## Agent skills` dans
  `.github/copilot-instructions.md`.
- L'index `.backlog/README.md` est maintenu à la main (pas de script générateur).
- `ROADMAP.md` reste la source de vérité du **séquencement** ; `.backlog/` est celle
  du **scope + statut**.

## Conséquences

- Plus de conflits de merge sur le backlog ; les agents ne chargent que le lot pertinent.
- `to-prd` / `to-issues` opèrent sur le backlog local sans fork des skills.
- Coût de migration unique ; les lots livrés sont archivés compacts.
- `docs/backlog.md` et `docs/backlog-archive.md` sont supprimés (contenu migré).
