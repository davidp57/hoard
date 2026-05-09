# Backlog — Hoard 🐦

Backlog produit pour Hoard — navigateur de médias et lecteur vidéo auto-hébergé.
Quand le travail démarre sur un sujet, créer une branche `feature/` depuis `develop`.
Quand un sujet est livré, mettre à jour `CHANGELOG.md` et passer le ticket en Terminé ici.

> Lots terminés depuis plus de 3 jours → [backlog-archive.md](backlog-archive.md)

---

## Calibration estimations

Facteur de marge actuel : **1,15** (15%) — valeur initiale, pas encore calibrée.

| Lot | Estimé Copilot | Réel Copilot | Ratio | Estimé gestion | Réel gestion | Ajustement |
| --- | --- | --- | --- | --- | --- | --- |

---

## Lots actifs

*Aucun lot actif pour le moment.*

---

### Hors lots

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-021 | Seek multi-niveaux unifié + raccourcis clavier étendus + modaux en plein écran | P2 | — | 2026-05-09 | | |
| BL-005 | Sélecteur de destination libre (arborescence filesystem) | P1 | — | 2026-04-12 | | |
| BL-007 | Tags arbitraires sur les fichiers + filtrage | P1 | — | 2026-04-12 | | |
| BL-011 | Authentification basique pour exposition hors LAN | P1 | — | 2026-04-12 | | |
| BL-002 | Tri dans la liste : taille + état de lecture | P2 | — | 2026-04-12 | | |
| BL-003 | Marquer manuellement vu / non vu | P2 | — | 2026-04-12 | | |
| BL-004 | Bouton plein écran + raccourci `F` | P2 | — | 2026-04-12 | | |
| BL-006 | Renommage de fichiers/dossiers depuis l'UI | P2 | — | 2026-04-12 | | |
| BL-008 | Sous-titres (`.srt` / `.ass` dans le même dossier) | P2 | — | 2026-04-12 | | |
| BL-009 | Rafraîchissement auto de la liste de fichiers | P2 | — | 2026-04-12 | | |
| BL-010 | Sélecteur de vitesse de lecture (0,5×, 1×, 1,5×, 2×) | P2 | — | 2026-04-12 | | |
| BL-015 | Progression de lecture multi-utilisateur | P2 | — | 2026-04-12 | | |
| BL-012 | Recherche dans les noms de fichiers | P3 | — | 2026-04-12 | | |
| BL-013 | Thème clair (toggle) | P3 | — | 2026-04-12 | | |
| BL-016 | Métadonnées vidéo dans l'UI (durée, résolution, codec) | P3 | — | 2026-04-12 | | |

---

## Détails

### BL-001 — Stabilize Backlog Triage

- **Dates**: `created=2026-04-12`, `completed=2026-04-13`

- **Why**: avoid leaving product decisions, bugs, and follow-up ideas only inside chat history.
- **Expected outcome**: a simple rule for when an item enters the backlog and how it is reprioritized.
- **Completed because**: the backlog workflow is now already applied in practice, with explicit status meanings, date rules, and recurring updates during ticket work.

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

### BL-004 — Proper Fullscreen Support

- **Dates**: `created=2026-04-12`

- **Why**: the current mobile overlay is useful but does not replace native fullscreen behavior in all cases.
- **Expected outcome**: add a fullscreen button and `F` shortcut with clean fallback behavior.
- **Attention point**: iPad and mobile browser limitations need explicit handling.

### BL-005 — Free-Move Destination Picker

- **Dates**: `created=2026-04-12`

- **Why**: predefined quick folders cover only a subset of real file-management flows.
- **Expected outcome**: browse the filesystem tree and choose any destination folder from the UI.
- **Benefit**: makes Hoard more usable as a real NAS file-management tool, not only as a player.

### BL-006 — Rename From The UI

- **Dates**: `created=2026-04-12`

- **Why**: file cleanup often requires quick renaming without opening SMB or another file manager.
- **Expected outcome**: rename files and folders safely from the web UI.
- **Attention point**: path safety and collision handling must stay explicit and predictable.

### BL-007 — File Tags And Tag Filtering

- **Dates**: `created=2026-04-12`

- **Why**: users need lightweight organization beyond watched / in-progress / watched.
- **Expected outcome**: store arbitrary tags in SQLite, display them in the list, and filter by tag.
- **Examples**: `to-finish`, `great`, `family`, `archive-later`.

### BL-008 — Subtitle Support

- **Dates**: `created=2026-04-12`

- **Why**: local media folders often contain sidecar subtitle files that are currently ignored.
- **Expected outcome**: detect `.srt` / `.ass` files in the same folder and expose them as selectable text tracks.
- **Attention point**: naming conventions and encoding issues need to be handled pragmatically.

### BL-009 — Auto-Refresh The File List

- **Dates**: `created=2026-04-12`

- **Why**: the UI currently refreshes the download folder after completed downloads, but general folder changes are still manual.
- **Expected outcome**: detect new files or external changes without requiring a full manual reload.
- **Options to discuss**: polling, SSE, or a simpler targeted refresh strategy.

### BL-010 — Playback Speed Selector

- **Dates**: `created=2026-04-12`

- **Why**: users increasingly expect variable playback speed in a media player.
- **Expected outcome**: expose a simple speed selector with a few useful presets.
- **Attention point**: keep the control compact enough for mobile and tablet layouts.

### BL-011 — Basic Authentication For External Exposure

- **Dates**: `created=2026-04-12`

- **Why**: HTTPS now exists, but exposure outside the LAN still needs an authentication layer.
- **Expected outcome**: a simple and safe authentication option for reverse-proxy or direct HTTPS deployments.
- **Attention point**: keep setup simple for self-hosted users and avoid turning the app into a full multi-account system prematurely.

### BL-012 — Search Across Filenames

- **Dates**: `created=2026-04-12`

- **Why**: raw filesystem browsing becomes less efficient as the media tree grows.
- **Expected outcome**: search across filenames under `MEDIA_ROOT` without introducing a metadata library.
- **Constraint**: preserve the project's philosophy of staying simple and filesystem-first.

### BL-013 — Light Theme Toggle

- **Dates**: `created=2026-04-12`

- **Why**: some environments and devices are easier to use with a light UI.
- **Expected outcome**: a simple theme toggle persisted locally.
- **Attention point**: keep the visual system coherent across desktop, mobile, and player states.

### BL-014 — PWA Support

- **Dates**: `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13`

- **Why**: Hoard already works well in Safari and desktop browsers, but a standalone install shell could reduce friction for home-screen launch and make the app feel less like a browser tab.
- **Expected outcome**: add a manifest and service worker so supported devices can install Hoard in standalone mode, with app-shell caching where it helps.
- **Attention point**: this should improve installability and launch ergonomics, not promise offline NAS video playback.

### BL-015 — Multi-User Watch Progress

- **Dates**: `created=2026-04-12`

- **Why**: a single watch-progress row per file is limiting when several people use the same Hoard instance.
- **Expected outcome**: separate watch progress by user while preserving the current lightweight architecture.
- **Attention point**: this has implications for authentication, settings, and UI complexity.

### BL-016 — Video Metadata In The UI

- **Dates**: `created=2026-04-12`

- **Why**: codec, duration, and resolution would help identify files before opening them.
- **Expected outcome**: display metadata in a lightweight detail pane or hover/card treatment.
- **Attention point**: any `ffprobe` usage must stay performant and avoid making folder navigation sluggish.

### BL-017 — Configurable Initial Sweep Per Folder

- **Dates**: `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13`

- **Functional rules**:
	- apply only when the file has no saved progress yet;
	- do not apply to already watched or already started videos;
	- allow `0` to mean "disabled";
	- folder override wins over the global default.
- **UX expectation**:
	- global default stays configured in Settings;
	- from the player, a single explicit action should save the current playback position as the default initial sweep for the current folder;
	- the player should avoid a permanent inline numeric editor for this folder-level action.
- **Data shape to discuss**: store a global `initial_sweep_seconds` setting plus a folder-level mapping keyed by relative folder path.
- **Attention point**: the rule should never override an existing saved position, and the player action should feel like a quick "use current position for this folder" command rather than a settings form.
- **Reopened because**: the first implementation works functionally, but the current player UI is too heavy for the intended use.
- **Acceptance signal**: while playing a file, the user can save the current time as the folder default in one explicit action, and brand-new videos in that folder start there while previously started videos still resume from real saved progress.

### BL-018 — Hide Controls In Fullscreen

- **Dates**: `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13`

- **Why**: visible controls take too much space in fullscreen playback, especially on tablets and smaller screens.
- **Expected outcome**: keep fullscreen auto-hide, but restrict the hide/show tap or click behavior to the intended bottom-centre zone near the controls.
- **Attention point**: user interaction outside that bottom-centre zone must not trigger hide/show side effects, otherwise normal clicks and taps become disruptive.
- **Reopened because**: the first implementation introduced a hitbox regression where hide/show behavior is triggered too broadly across the fullscreen video area.
- **Reopened again because**: single taps on the right side can still fall through to centre actions, so the fullscreen controls and play/pause hitboxes need to be narrowed further.
- **Acceptance signal**: in fullscreen, clicking or tapping outside the bottom-centre control zone does not toggle the controls, while the intended bottom-centre area still does.

### BL-019 — Investigate Broader Native Codec Playback

- **Dates**: `created=2026-04-12`, `started=2026-04-12`, `completed=2026-04-12`

- **Why**: some devices currently fall back to transcoding, for example H.265 to H.264 on iPad, even though native playback support may exist for part of the matrix of codecs, containers, browser engines, and hardware.
- **Expected outcome**: produce a clear compatibility matrix and ship a first metadata-driven decision path so Hoard can prefer native playback over transcoding when browser support is actually confirmed.
- **Scope**: codec support, container support, browser differences, media source constraints, an on-demand metadata endpoint, and practical detection strategy in the frontend/backend.
- **Attention point**: keep `/api/transcode` as the safety net even after browser-side probing is added.

### BL-021 — Unified Multi-Level Seek And Extended Keyboard Shortcuts

- **Dates**: `created=2026-05-09`

- **Why**: seek is currently hardcoded at 10s (keyboard) and configured separately for touch double-tap zones; there is no consistency between input methods, and keyboard shortcuts cover only basic playback while all other player actions (move, delete, cut, aspect ratio, markers, sweep, navigation) are mouse/touch-only.
- **Expected outcome**:
  1. **Unified 4-level seek** — one set of 4 configurable durations (`seek_short=10s`, `seek_medium=30s`, `seek_long=60s`, `seek_xlong=120s`) applied consistently to both keyboard and touch double-tap:
     - Keyboard: `←/→` (short), `Shift+←/→` (medium), `Ctrl+←/→` (long), `Alt+←/→` (x-long)
     - Double-tap left zone → medium (rewind)
     - Double-tap right zone, bottom third → medium (forward)
     - Double-tap right zone, middle third → long (forward)
     - Double-tap right zone, top third → x-long (forward)
     - Player skip buttons: driven by `seek_short` and `seek_medium`
     - Settings: replace the current separate `doubletap_right_*` and `doubletap_left` inputs with the 4 unified seek inputs
  2. **Extended keyboard shortcuts** — new bindings active when a video is open:
     - `M` → mute toggle (bug fix: was documented but missing from the keydown handler)
     - `A` → aspect ratio cycle
     - `I` / `O` → set IN / OUT marker at current position
     - `C` → open Cut modal
     - `D` → open Move modal
     - `Delete` → delete with confirmation
     - `S` → save current position as folder start offset
     - `PageDown` / `PageUp` → next / previous video in folder
     - `?` → show keyboard shortcut reference overlay
  3. **Modals usable in native fullscreen** — convert move, cut, and delete confirmation overlays to `<dialog>.showModal()` so they appear above the native fullscreen element without exiting fullscreen.
- **Functional rules**:
  - Keyboard shortcuts that require an open video (`A`, `I`, `O`, `C`, `D`, `Delete`, `S`) are no-ops when `currentFile` is null.
  - `Delete` and `D` from the keyboard: after completion, auto-advance to the next video in folder if one exists.
  - `window.confirm()` in `confirmDelete` must be replaced by a `<dialog>` confirmation (Chrome silently blocks `window.confirm()` during native fullscreen).
  - `doubletap_left` and `doubletap_right_*` settings keys are removed; their stored values are ignored after migration (no migration needed — defaults are overwritten on first save).
- **Attention points**:
  - `Alt+←/→` may conflict with browser history navigation in some configurations — test on Chrome, Firefox, and SteamDeck.
  - `<dialog>.showModal()` is fully supported in all evergreen browsers; verify behavior inside the faux-fullscreen CSS fallback as well.
  - The shortcut reference dialog (`?`) should be a lightweight static table, not a dynamic component.
- **Acceptance signal**: from keyboard alone, a user can play/pause, seek at 4 speeds, adjust volume and mute, toggle aspect, set markers, cut, move, delete, save folder sweep, and navigate to the next/previous video — all without exiting native fullscreen.

### BL-020 — Native Fullscreen Broken On Touch-Capable Desktop Browsers

- **Dates**: `created=2026-05-09`

- **Why**: `toggleFullscreen()` uses `navigator.maxTouchPoints > 0` as a second condition to force faux-fullscreen (CSS overlay). This was originally intended for iPad/Safari where `document.fullscreenEnabled` is already `false`. However it also fires on any touch-capable device that actually supports native fullscreen (e.g. SteamDeck running Firefox), causing native fullscreen to never be requested even though the browser supports it.
- **Expected outcome**: native fullscreen works on Firefox/SteamDeck and any other touch-capable desktop browser. iPad continues to use faux-fullscreen because `fullscreenEnabled` remains false on Safari.
- **Scope**: `toggleFullscreen()` in `frontend/index.html` — remove the `|| navigator.maxTouchPoints > 0` branch; rely solely on `!document.fullscreenEnabled`.

## Lots terminés

> Lots terminés depuis plus de 3 jours → [backlog-archive.md](backlog-archive.md)

- **BL-020** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Native fullscreen now works on touch-capable desktop browsers (SteamDeck/Firefox): removed the overly-broad `navigator.maxTouchPoints > 0` condition from `toggleFullscreen()`; rely solely on `!document.fullscreenEnabled` to decide between native and faux-fullscreen. iPad/Safari unaffected because `fullscreenEnabled` is already `false` there.

- **BL-014** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Optional PWA install shell delivered with a manifest, a minimal service worker, standalone-launch polish, and explicit limits so app installability does not imply offline NAS playback.
- **BL-001** — `created=2026-04-12`, `completed=2026-04-13` — Backlog triage process considered established: ticket states, date fields, and regular backlog updates are now already part of the working workflow.
- **BL-018** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Fullscreen controls hitbox follow-up delivered: simple taps on the side zones no longer fall through to centre actions, and only a narrow bottom-centre strip can toggle controls.
- **BL-017** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Folder initial sweep UX simplified: the player now exposes a single compact action that saves the current playback position as the folder default start, without the previous inline editor.
- **BL-019** — `created=2026-04-12`, `started=2026-04-12`, `completed=2026-04-12` — Native playback investigation and first implementation delivered with a bilingual compatibility note, a new `/api/media-info` ffprobe endpoint, and player-side probing via `canPlayType()` plus `MediaCapabilities` before falling back to `/api/transcode`.
- **BL-101** — `created=2026-04-05`, `started=2026-04-05`, `completed=2026-04-06` — Web video download delivered in v2.0 with a bookmarklet, yt-dlp integration, smart source detection, server-side HTML sniffing fallback, cookie / referer passthrough, and SSRF protection.
- **BL-102** — `created=2026-04-06`, `started=2026-04-06`, `completed=2026-04-06` — Sequential download queue delivered in v2.0 with live queue modal, active badge, stop / cancel action, two-phase preparation, automatic temporary file cleanup, and download-folder auto-refresh.
- **BL-103** — `created=2026-04-06`, `started=2026-04-06`, `completed=2026-04-06` — Native HTTPS delivered in v2.0 via `SSL_CERTFILE` / `SSL_KEYFILE`, with Docker and installation documentation.