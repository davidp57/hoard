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
| [PAD-PROFILES](PAD-PROFILES/PRD.md) — Des profils de manette, dont un pour la seule main droite du Steam Frame (BL-141 ; reste l'essai sur le Frame) | 🧑 |
| [PAD-ZOOM](PAD-ZOOM/PRD.md) — Zoomer dans une vidéo à la manette, comme dans PadView (couche R2 sur vidéo plate BL-140 ; reste l'essai sur le Frame) | 🧑 |
| [PAD-LEFT-HAND](PAD-LEFT-HAND/PRD.md) — La main gauche règle ce qu'on regarde (volume et vitesse au stick gauche, sauts à la croix BL-138 ; convention manette commune avec PadView BL-139 ; reste l'essai sur le Frame) | 🧑 |
| [FIX-UI-SCALE](FIX-UI-SCALE/PRD.md) — Une taille apparente constante en plein écran (interface en `rem`, échelle à la racine BL-137 ; reste l'essai sur le Frame) | 🧑 |
| [VR-IMMERSIVE](VR-IMMERSIVE/PRD.md) — Le relief dans le casque par WebXR (session immersive BL-136 mergée ; en pause : pas de WebXR dans le navigateur du Frame) | 🧑 |
| [CLIENT-NATIVE](CLIENT-NATIVE/PRD.md) — Client natif Flutter pour Steam Deck, Steam Frame et Windows (faisabilité BL-104 ✅, puis BL-107..117) | 🔄 |
| [FEAT-ADVANCED](FEAT-ADVANCED/PRD.md) — Fonctionnalités avancées (thème clair BL-013, multi-utilisateur BL-015) | ⬜ |
| [ARCH-PERF](ARCH-PERF/PRD.md) — Architecture & Performance (split `main.py` BL-041, transcodage HW BL-042) | ⬜ |

## Lots archivés

Voir [`archive/`](archive/). Les lignes sont ajoutées ici au fur et à mesure des archivages.

| Lot | Statut | Terminé |
|-----|--------|---------|
| [VR-COMFORT](archive/VR-COMFORT.md) — Que la profondeur soit juste, et réglable en regardant | ✅ | 2026-09-22 |
| [PAD-SBS-UI](archive/PAD-SBS-UI.md) — Toute l'interface en côte à côte, sur bascule | ✅ | 2026-09-22 |
| [SORT-WATCHED](archive/SORT-WATCHED.md) — Trier par date de dernier visionnage | ✅ | 2026-09-21 |
| [SEC-SESSION](archive/SEC-SESSION.md) — Session par cookie et jeton pour la bookmarklet | ✅ | 2026-09-21 |
| [SEC-AUTH](archive/SEC-AUTH.md) — Une instance ouverte doit se voir | ✅ | 2026-09-21 |
| [PAD-VR](archive/PAD-VR.md) — Piloter le VR à la manette en voyant ce qu'on règle | ✅ | 2026-09-21 |
| [FIX-XR-DISPLAY](archive/FIX-XR-DISPLAY.md) — Hoard utilisable sur lunettes XR en 3840×1080 | ✅ | 2026-09-21 |
| [FEAT-VR180](archive/FEAT-VR180.md) — Lecture des vidéos 180° SBS dans le lecteur web | ✅ | 2026-09-21 |
| [MOVE-COLLISION](archive/MOVE-COLLISION.md) — Déplacer vers une destination occupée | ✅ | 2026-09-15 |
| [PAD-REACH](archive/PAD-REACH.md) — Toute l'UI atteignable à la manette | ✅ | 2026-09-14 |
| [DL-RETRY](archive/DL-RETRY.md) — Relancer un téléchargement depuis l'historique | ✅ | 2026-08-25 |
| [DL-INTEGRITY](archive/DL-INTEGRITY.md) — Un téléchargement « terminé » doit exister | ✅ | 2026-08-25 |
| [OPS-VISIBILITY](archive/OPS-VISIBILITY.md) — Traçabilité & exploitation | ✅ | 2026-08-24 |
| [FEAT-GALLERY](archive/FEAT-GALLERY.md) — Galeries d'images | ✅ | 2026-06-27 |
| [KBD-DPAD-PARITY](archive/KBD-DPAD-PARITY.md) — Clavier ↔ pad : équivalence navigation | ✅ | 2026-06-23 |
| [INPUT-HARMONIZATION](archive/INPUT-HARMONIZATION.md) — Harmonisation clavier / pad / touch | ✅ | 2026-05-19 |
| [ALT-READERS](archive/ALT-READERS.md) — Lecteurs alternatifs (images, archives, PDF, audio) | ✅ | 2026-05-15 |
| [MULTI-SEGMENTS](archive/MULTI-SEGMENTS.md) — Sélection multi-zones et export | ✅ | 2026-05-15 |
| [GAMEPAD-FIXES](archive/GAMEPAD-FIXES.md) — Correctifs gamepad post-recette | ✅ | 2026-05-15 |
| [SECURITY-QUALITY-UX](archive/SECURITY-QUALITY-UX.md) — Sécurité, Qualité & UX | ✅ | 2026-06-14 |
| [UI-BROWSER-PLAYER](archive/UI-BROWSER-PLAYER.md) — Extensions browser & player | ✅ | 2026-05-09 |
| [FOUNDATION](archive/FOUNDATION.md) — Socle v1 / v2.0 (Lots 1–3) | ✅ | 2026-05-09 |
