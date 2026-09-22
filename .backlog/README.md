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
| [SEC-AUTH](SEC-AUTH/PRD.md) — Une instance ouverte doit se voir (contrôle de santé BL-105, annonce de l'état d'authentification BL-106) | ✅ |
| [CLIENT-NATIVE](CLIENT-NATIVE/PRD.md) — Client natif Flutter pour Steam Deck, Steam Frame et Windows (faisabilité BL-104 ✅, puis BL-107..117) | 🔄 |
| [SEC-SESSION](SEC-SESSION/PRD.md) — Session par cookie et jeton pour la bookmarklet (écran de connexion BL-123, bookmarklet cassée par l'auth BL-124) | ✅ |
| [VR-COMFORT](VR-COMFORT/PRD.md) — Que la profondeur soit juste, et réglable en regardant (champ de vision BL-133, convergence au stick BL-134, bords comprimés BL-135) | ✅ |
| [PAD-SBS-UI](PAD-SBS-UI/PRD.md) — Toute l'interface en côte à côte, sur bascule (miroir global BL-130, états vivants BL-131, médias BL-132) | ✅ |
| [PAD-VR](PAD-VR/PRD.md) — Piloter le VR à la manette en voyant ce qu'on règle (fenêtres lisibles en côte à côte BL-127, couche VR sous R2 BL-128, convergence par fichier BL-129) | ✅ |
| [FIX-XR-DISPLAY](FIX-XR-DISPLAY/PRD.md) — Hoard utilisable sur lunettes XR en 3840×1080 (fenêtres manette à l'échelle BL-126 ✅, ratio côte à côte BL-125 ✅) | ✅ |
| [FEAT-VR180](FEAT-VR180/PRD.md) — Lecture des vidéos 180° SBS dans le lecteur web (socle BL-119, sortie SBS BL-120, détection BL-121, réglages BL-122) | ✅ |
| [FEAT-ADVANCED](FEAT-ADVANCED/PRD.md) — Fonctionnalités avancées (thème clair BL-013, multi-utilisateur BL-015) | ⬜ |
| [ARCH-PERF](ARCH-PERF/PRD.md) — Architecture & Performance (split `main.py` BL-041, transcodage HW BL-042) | ⬜ |
| [FEAT-GALLERY](FEAT-GALLERY/PRD.md) — Galeries d'images (dossier comme média opaque, comme une archive) | ✅ |
| [OPS-VISIBILITY](OPS-VISIBILITY/PRD.md) — Traçabilité & exploitation (historique de téléchargement BL-075, rétention des logs BL-076, redémarrage depuis l'UI BL-077, résilience du worker BL-078) | ✅ |
| [DL-INTEGRITY](DL-INTEGRITY/PRD.md) — Un téléchargement « terminé » doit exister (skip silencieux BL-079, destination visible BL-080, sûreté du test de redémarrage BL-081, sélecteur de dossier BL-082, isolation réseau des tests BL-083) | ✅ |
| [DL-RETRY](DL-RETRY/PRD.md) — Relancer un téléchargement depuis l'historique (BL-084) | ✅ |
| [SORT-WATCHED](SORT-WATCHED/PRD.md) — Trier par date de dernier visionnage (BL-085, tri mémorisé BL-118) | ✅ |
| [PAD-REACH](PAD-REACH/PRD.md) — Toute l'UI atteignable à la manette (modals BL-088, actions inertes BL-087, marquer vu BL-003, menu contextuel BL-086) | ✅ |
| [MOVE-COLLISION](MOVE-COLLISION/PRD.md) — Déplacer vers une destination occupée (choix écraser/annuler BL-090, métadonnées des dossiers BL-091, job en échec BL-092, curseur manette générique BL-093) | ✅ |

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
