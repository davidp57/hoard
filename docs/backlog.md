# Backlog — Hoard 🐦

Backlog produit pour Hoard — navigateur de médias et lecteur vidéo auto-hébergé.
Quand le travail démarre sur un sujet, créer une branche `feature/` depuis `develop`.
Quand un sujet est livré, mettre à jour `CHANGELOG.md` et passer le ticket en Terminé ici.

> Lots terminés depuis plus de 3 jours → [backlog-archive.md](backlog-archive.md)

---

## Calibration estimations

Facteur de marge actuel : **0,40**.

| Lot | Estimé Copilot | Réel Copilot | Ratio | Estimé gestion | Réel gestion | Ajustement |
| --- | --- | --- | --- | --- | --- | --- |

> - Tickets de finition / tests simples → estimation de référence 3–5 min, pas 10–20 min.
> - Avant d'estimer un ticket de « review fix », vérifier si le problème existe réellement.
> - Pour les tickets d'implémentation technique pure, appliquer un facteur **0,60** par rapport à l'estimation initiale naïve.

---

## Lots actifs

### Lot 5 — Fonctionnalités avancées (~150 min : 135 min Copilot + 15 min gestion)

> Dépendance interne : BL-015 dépend de BL-011 (la progression multi-utilisateur présuppose une couche d'authentification) — exécuter BL-011 en premier.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-002 | Tri dans la liste : taille + état de lecture | P2 | 10 min | 2026-04-12 | | |
| BL-003 | Marquer manuellement vu / non vu | P2 | 10 min | 2026-04-12 | | |
| BL-006 | Renommage de fichiers/dossiers depuis l'UI | P2 | 15 min | 2026-04-12 | | |
| BL-008 | Sous-titres (`.srt` / `.ass` dans le même dossier) | P2 | 25 min | 2026-04-12 | | |
| BL-013 | Thème clair (toggle) | P3 | 20 min | 2026-04-12 | | |
| BL-011 | Authentification basique pour exposition hors LAN | P1 | 20 min | 2026-04-12 | | |
| BL-015 | Progression de lecture multi-utilisateur *(dépend de BL-011)* | P2 | 35 min | 2026-04-12 | | |

---

### Hors lots

*Aucun ticket hors lot pour le moment.*

---

## Détails

### BL-002 — Sort Controls In The File List

- **Dates**: `created=2026-04-12`

- **Why**: the file list already supports sorting by name and modified date, but larger folders still need size and watch-status sorting to make the controls feel complete.
- **Expected outcome**: extend the existing sort UI so users can sort by name, modified date, size, and watch status, with a clear active state.
- **Attention point**: keep the behavior simple on both desktop and touch devices, and avoid turning the sort bar into a crowded toolbar.

### BL-003 — Manual Watched / Unwatched Toggle

- **Dates**: `created=2026-04-12`

- **Why**: users sometimes need to fix watch status manually without reopening the video.
- **Expected outcome**: allow a quick explicit action from the file list or context UI.
- **Attention point**: define whether the action resets stored playback position or only the seen threshold state.

### BL-006 — Rename From The UI

- **Dates**: `created=2026-04-12`

- **Why**: file cleanup often requires quick renaming without opening SMB or another file manager.
- **Expected outcome**: rename files and folders safely from the web UI.
- **Attention point**: path safety and collision handling must stay explicit and predictable.

### BL-008 — Subtitle Support

- **Dates**: `created=2026-04-12`

- **Why**: local media folders often contain sidecar subtitle files that are currently ignored.
- **Expected outcome**: detect `.srt` / `.ass` files in the same folder and expose them as selectable text tracks.
- **Attention point**: naming conventions and encoding issues need to be handled pragmatically.

### BL-011 — Basic Authentication For External Exposure

- **Dates**: `created=2026-04-12`

- **Why**: HTTPS now exists, but exposure outside the LAN still needs an authentication layer.
- **Expected outcome**: a simple and safe authentication option for reverse-proxy or direct HTTPS deployments.
- **Attention point**: keep setup simple for self-hosted users and avoid turning the app into a full multi-account system prematurely.

### BL-013 — Light Theme Toggle

- **Dates**: `created=2026-04-12`

- **Why**: some environments and devices are easier to use with a light UI.
- **Expected outcome**: a simple theme toggle persisted locally.
- **Attention point**: keep the visual system coherent across desktop, mobile, and player states.

### BL-015 — Multi-User Watch Progress

- **Dates**: `created=2026-04-12`

- **Why**: a single watch-progress row per file is limiting when several people use the same Hoard instance.
- **Expected outcome**: separate watch progress by user while preserving the current lightweight architecture.
- **Attention point**: this has implications for authentication, settings, and UI complexity.

### BL-024 — Gamepad Support (Steam Deck, iPhone + Controller, Xbox, etc.)

- **Dates**: `created=2026-05-09`

- **Why**: Hoard is used on touch-capable devices including the Steam Deck and iPad with Bluetooth controller. No gamepad input is currently supported, forcing users to switch between controller and touch/mouse for navigation and player control.
- **Expected outcome**:
  1. **Gamepad API integration** — poll `navigator.getGamepads()` via a `requestAnimationFrame` loop; detect button press edges (pressed this frame, not last); suspend the loop when the tab is hidden (Page Visibility API).
  2. **4-layer system** — L1 and R1 bumpers act as modifiers; four independent layers: base / L1 / R1 / L1+R1.
  3. **Player controls** (when a video is open):
     - Base: A → play/pause, B → close player, X → toggle watched, Y → fullscreen
     - D-pad ←/→: seek by `cfg.seek_medium` (base), `cfg.seek_long` (L1), `cfg.seek_xlong` (R1)
     - D-pad ↑/↓: volume ±10% (base), previous/next file in list (L1), jump to 25%/75% (R1)
     - Stick left X → **analog scrubbing**: visual update every frame (`seekbarFill`, `seekbarThumb`), `video.currentTime` throttled to ~100ms; mirrors the existing pointer-drag seekbar behavior
     - Stick right Y → analog volume
     - L1+R1 + A/X/Y → jump to 0% / 50% / 100%
     - L1 + X → aspect ratio toggle; L1 + A → subtitles (no-op if BL-008 not delivered)
     - R1 + A/B/X → move to predefined folder #1/#2/#3
  4. **File browser navigation** (when no video is open):
     - D-pad ↑/↓ / stick left Y → move cursor through file list, auto-scroll
     - A → open file or folder, B → go up one level, Start → open settings
  5. **Steam Deck / Firefox compatibility** — Firefox only fires `gamepadconnected` after a user interaction. On page load and on `visibilitychange`, scan `navigator.getGamepads()` for already-connected devices. Show a persistent subtle toast « 🎮 Appuyez sur un bouton pour activer la manette » if a gamepad is detected but polling has not yet started (identified by `mapping === ''`).
  6. **Connection toasts** — brief toast on `gamepadconnected` / `gamepaddisconnected`.
  7. **Layer HUD** — small corner badge showing the active modifier (L1 / R1 / L1+R1) while a bumper is held.
  8. **Mapping overlay** — triggered by Select or R1+Start; semi-transparent overlay listing all actions per layer, generated dynamically from the current mapping.
  9. **Haptic feedback** (optional, Chrome only) — short vibration on play/pause, watched toggle, and long seeks via `gamepad.vibrationActuator`.
  10. **Configurable mapping** — mapping stored as JSON under key `gamepad_mapping` in the `settings` SQLite table (initialized in `init_db()`). Settings UI: « Manette » tab with action list, Rebind button, deadzone slider, haptic toggle, gamepad on/off toggle.
- **Functional rules**: All gamepad actions mirror existing JS functions (`skip()`, `togglePlay()`, `toggleFullscreen()`, etc.). Seek values come from `cfg.seek_medium/long/xlong` (co-delivered with BL-021 in the same lot). Analog scrubbing respects cut IN/OUT boundaries. Gamepad actions are no-ops when the relevant UI state is not active (e.g., player actions are ignored when no file is open).
- **Attention points**: Stick deadzone is configurable (default 20%); scrubbing throttle must not conflict with the `timeupdate` handler that normally syncs the seekbar. `vibrationActuator` is Chrome-only — guard with feature detection. Trigger axes (buttons 6/7) are inconsistently mapped across platforms — avoid relying on them.
- **Files**: `frontend/index.html` (Gamepad engine, CSS HUD/overlay, analog scrubbing), `backend/main.py` (`init_db()`: `gamepad_mapping` key), `docs/user-guide.en.md`, `docs/user-guide.fr.md`.

---

## Lots terminés

> Lots terminés depuis plus de 3 jours → [backlog-archive.md](backlog-archive.md)

### Lot 4 — UI Browser & Player Extensions

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