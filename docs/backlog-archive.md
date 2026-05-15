# Archive backlog — Hoard 🐦

Ce fichier contient les lots terminés depuis plus de 3 jours, archivés depuis [`backlog.md`](backlog.md).

---

## Lots archivés

### Lot 4 — UI Browser & Player Extensions

- **BL-040** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Racine de navigation par défaut : colonne `is_default` en base, endpoint `POST /api/home-roots/{id}/set-default`, navigation directe au démarrage et après PIN, indicateur visuel dans les Paramètres. `openRootPicker()` ouvre la browse modal au lieu d'utiliser `currentPath` silencieusement.

- **BL-024** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Support gamepad complet : Gamepad API, 4 couches L1/R1, contrôles lecteur, navigation navigateur, scrubbing analogique, HUD badge, overlay aide, toasts, haptique Chrome, section Paramètres Manette. Backend : clés `gamepad_enabled/deadzone/haptic/mapping` en SQLite.

- **BL-023** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Liste de dossiers « home » multiples avec gestion backend (`home_roots`) et écran de sélection UI.
- **BL-009** — `created=2026-04-12`, `started=2026-05-09`, `completed=2026-05-09` — Rafraîchissement auto de la liste toutes les 30 s (onglet visible + vidéo en pause + pas de recherche active).
- **BL-010** — `created=2026-04-12`, `started=2026-05-09`, `completed=2026-05-09` — Sélecteur de vitesse de lecture (0,5×/1×/1,5×/2×), réinitialisé à chaque ouverture.
- **BL-016** — `created=2026-04-12`, `started=2026-05-09`, `completed=2026-05-09` — Métadonnées vidéo (codec, résolution, durée, bitrate) via `ffprobe` affichées sous le titre du fichier en cours.
- **BL-012** — `created=2026-04-12`, `started=2026-05-09`, `completed=2026-05-09` — Recherche récursive dans les noms de fichiers via `GET /api/search`, champ dans la barre de tri.
- **BL-005** — `created=2026-04-12`, `started=2026-05-09`, `completed=2026-05-09` — Sélecteur de destination libre (parcours de l'arborescence filesystem) dans le modal de déplacement.
- **BL-007** — `created=2026-04-12`, `started=2026-05-09`, `completed=2026-05-09` — Tags arbitraires sur les fichiers (table `file_tags`), badges dans la liste, barre de filtrage par tag dynamique.

### Lots 1–3

- **BL-026** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Contrôles plein écran : les boutons skip, les touches clavier et le swipe horizontal affichent désormais tous un toast de seek ; le reveal de la barre de contrôles est limité aux 10 % bas de l'écran ; `mousemove` ne déclenche plus la révélation hors de la zone basse.
- **BL-021** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Seek unifié 4 niveaux (`seek_short/medium/long/xlong` configurables), raccourcis clavier étendus (Shift/Ctrl/Alt+←/→, A, M, I/O, C, D, Suppr, S, PageDown/PageUp, ?), et toutes les boîtes de dialogue (déplacement, découpe, suppression, aide) converties en `<dialog>.showModal()` pour rester visibles au-dessus du plein écran natif.
- **BL-025** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Icône du bouton aspect ratio remplacée par une icône SVG de cadre distincte, évitant la confusion avec le bouton plein écran.
- **BL-022** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Paramètre `transcode_enabled` ajouté (défaut : activé). Quand désactivé, le player utilise toujours `/api/stream` et n'appelle jamais `/api/transcode`.
- **BL-020** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Native fullscreen now works on touch-capable desktop browsers (SteamDeck/Firefox): removed the overly-broad `navigator.maxTouchPoints > 0` condition from `toggleFullscreen()`; rely solely on `!document.fullscreenEnabled` to decide between native and faux-fullscreen. iPad/Safari unaffected because `fullscreenEnabled` is already `false` there.
- **BL-014** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Optional PWA install shell delivered with a manifest, a minimal service worker, standalone-launch polish, and explicit limits so app installability does not imply offline NAS playback.
- **BL-001** — `created=2026-04-12`, `completed=2026-04-13` — Backlog triage process considered established: ticket states, date fields, and regular backlog updates are now already part of the working workflow.
- **BL-018** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Fullscreen controls hitbox follow-up delivered: simple taps on the side zones no longer fall through to centre actions, and only a narrow bottom-centre strip can toggle controls.
- **BL-017** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Folder initial sweep UX simplified: the player now exposes a single compact action that saves the current playback position as the folder default start, without the previous inline editor.
- **BL-019** — `created=2026-04-12`, `started=2026-04-12`, `completed=2026-04-12` — Native playback investigation and first implementation delivered with a bilingual compatibility note, a new `/api/media-info` ffprobe endpoint, and player-side probing via `canPlayType()` plus `MediaCapabilities` before falling back to `/api/transcode`.
- **BL-101** — `created=2026-04-05`, `started=2026-04-05`, `completed=2026-04-06` — Web video download delivered in v2.0 with a bookmarklet, yt-dlp integration, smart source detection, server-side HTML sniffing fallback, cookie / referer passthrough, and SSRF protection.
- **BL-102** — `created=2026-04-06`, `started=2026-04-06`, `completed=2026-04-06` — Sequential download queue delivered in v2.0 with live queue modal, active badge, stop / cancel action, two-phase preparation, automatic temporary file cleanup, and download-folder auto-refresh.
- **BL-103** — `created=2026-04-06`, `started=2026-04-06`, `completed=2026-04-06` — Native HTTPS delivered in v2.0 via `SSL_CERTFILE` / `SSL_KEYFILE`, with Docker and installation documentation.
