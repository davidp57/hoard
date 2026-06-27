# Backlog — Hoard 🐦

Backlog par lot. Les lots **actifs** sont des dossiers `.backlog/<LOT-ID>/` (PRD +
tickets) ; les lots **terminés** sont compactés dans `.backlog/archive/<LOT-ID>.md`.
Le **séquencement** vit dans [ROADMAP](../ROADMAP.md) ; cet index est la source de
vérité du **scope + statut**.

Convention détaillée : [`docs/agents/issue-tracker.md`](../docs/agents/issue-tracker.md).

## Légende

- **Status** : ⬜ ready · 🔄 in-progress · 🧑 waiting-human · ✅ done · 🚫 wontfix
- Les IDs de tickets restent `BL-NNN` (schéma global historique, référencé dans les
  commits, `CHANGELOG.md`, `ROADMAP.md` et les docs).

## Lots actifs

| Lot | Statut |
|-----|--------|
| [FEAT-ADVANCED](FEAT-ADVANCED/PRD.md) — Fonctionnalités avancées (thème clair BL-013, multi-utilisateur BL-015) | ⬜ |
| [ARCH-PERF](ARCH-PERF/PRD.md) — Architecture & Performance (split `main.py` BL-041, transcodage HW BL-042) | ⬜ |
| [FEAT-GALLERY](FEAT-GALLERY/PRD.md) — Galeries d'images (dossier comme média opaque, comme une archive) | ✅ |

## Lots archivés

Voir [`archive/`](archive/). Les lignes sont ajoutées ici au fur et à mesure des archivages.

| Lot | Statut | Terminé |
|-----|--------|---------|
| [KBD-DPAD-PARITY](archive/KBD-DPAD-PARITY.md) — Clavier ↔ pad : équivalence navigation | ✅ | 2026-06-23 |
| [INPUT-HARMONIZATION](archive/INPUT-HARMONIZATION.md) — Harmonisation clavier / pad / touch | ✅ | 2026-05-19 |
| [ALT-READERS](archive/ALT-READERS.md) — Lecteurs alternatifs (images, archives, PDF, audio) | ✅ | 2026-05-15 |
| [MULTI-SEGMENTS](archive/MULTI-SEGMENTS.md) — Sélection multi-zones et export | ✅ | 2026-05-15 |
| [GAMEPAD-FIXES](archive/GAMEPAD-FIXES.md) — Correctifs gamepad post-recette | ✅ | 2026-05-15 |
| [SECURITY-QUALITY-UX](archive/SECURITY-QUALITY-UX.md) — Sécurité, Qualité & UX | ✅ | 2026-06-14 |
| [UI-BROWSER-PLAYER](archive/UI-BROWSER-PLAYER.md) — Extensions browser & player | ✅ | 2026-05-09 |
| [FOUNDATION](archive/FOUNDATION.md) — Socle v1 / v2.0 (Lots 1–3) | ✅ | 2026-05-09 |
