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

### Lot 2 — Gamepad (~85 min : 70 min Copilot + 15 min gestion) — dépend du Lot 1

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-024 | Contrôle gamepad (manette, Steam Deck, iPhone + controller) | P2 | 70 min | 2026-05-09 | | |

### Lot 4 — UI Browser & Player Extensions (~165 min : 150 min Copilot + 15 min gestion)

> BL-004 fusionné dans BL-021 (Lot 1). Dépendance interne : BL-005 dépend de BL-023 (le sélecteur de destination doit connaître la racine active) — exécuter BL-023 en premier.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-009 | Rafraîchissement auto de la liste de fichiers | P2 | 15 min | 2026-04-12 | | |
| BL-010 | Sélecteur de vitesse de lecture (0,5×, 1×, 1,5×, 2×) | P2 | 10 min | 2026-04-12 | | |
| BL-016 | Métadonnées vidéo dans l'UI (durée, résolution, codec) | P3 | 15 min | 2026-04-12 | | |
| BL-012 | Recherche dans les noms de fichiers | P3 | 20 min | 2026-04-12 | | |
| BL-023 | Liste de dossiers « home » (plusieurs racines de navigation) | P2 | 25 min | 2026-05-09 | | |
| BL-005 | Sélecteur de destination libre (arborescence filesystem) | P1 | 30 min | 2026-04-12 | | |
| BL-007 | Tags arbitraires sur les fichiers + filtrage | P1 | 35 min | 2026-04-12 | | |

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

### BL-001 — Stabilize Backlog Triage

- **Dates**: `created=2026-04-12`, `completed=2026-04-13`

- **Why**: avoid leaving product decisions, bugs, and follow-up ideas only inside chat history.
- **Expected outcome**: a simple rule for when an item enters the backlog and how it is reprioritized.
- **Completed because**: the backlog workflow is now already applied in practice, with explicit status meanings, date rules, and recurring updates during ticket work.

### BL-023 — Multiple Home Folders

- **Dates**: `created=2026-05-09`

- **Why**: currently a single `MEDIA_ROOT` is the only navigation root. Users who organise content across several top-level directories (e.g. `/media/movies`, `/media/series`, `/media/music`) must either merge them under one root or navigate manually.
- **Expected outcome**: configure a list of named home folders (name + path pairs); the UI shows a home screen listing all of them so users jump directly to any root without nesting everything.
- **Attention point**: all paths must still pass through `safe_path()` scoped to each declared root; each root is independent (no cross-root moves).

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

### BL-004 — Proper Fullscreen Support *(fusionné dans BL-021)*

- **Dates**: `created=2026-04-12`

- **Why**: the current mobile overlay is useful but does not replace native fullscreen behavior in all cases.
- **Expected outcome**: add a fullscreen button and `F` shortcut with clean fallback behavior.
- **Attention point**: iPad and mobile browser limitations need explicit handling.
- **Note**: absorbed into BL-021 (keyboard shortcuts lot). The native fullscreen behavior fix was already delivered by BL-020.

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

### BL-022 — Option To Disable Transcoding (Direct Native Playback)

- **Dates**: `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09`

- **Why**: `/api/transcode` is sometimes invoked unnecessarily, even when the browser can play the original format natively. Transcoding is CPU-intensive and the NAS lacks the power for it; even a short transcode stall degrades the viewing experience.
- **Expected outcome**: add a boolean setting `transcode_enabled` (default `true`). When disabled, the player always streams the raw file via `/api/stream` regardless of codec or container, and never calls `/api/transcode`. The setting is toggleable from the Settings panel.
- **Functional rules**:
  - When `transcode_enabled = false`, skip `canPlayType()` / `MediaCapabilities` probing and go straight to `/api/stream`.
  - The transcode endpoint remains available (no removal) but is simply not called.
  - The setting persists in the `settings` SQLite table like all other settings.
- **Attention point**: disabling transcoding may cause playback to fail silently for formats the browser truly cannot handle; document this tradeoff clearly in the UI (tooltip or note near the toggle).
- **Acceptance signal**: with `transcode_enabled = false`, opening any video never triggers a call to `/api/transcode`; with `transcode_enabled = true`, the existing probing logic is unchanged.

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

### BL-021 — Unified Multi-Level Seek, Extended Keyboard Shortcuts & Fullscreen Button *(absorbe BL-004)*

- **Dates**: `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09`

- **Why**: seek is currently hardcoded at 10s (keyboard) and configured separately for touch double-tap zones; there is no consistency between input methods, and keyboard shortcuts cover only basic playback while all other player actions (move, delete, cut, aspect ratio, markers, sweep, navigation) are mouse/touch-only. BL-004 (fullscreen button + `F` shortcut) is included here since `F` is already part of the keyboard handler and the fullscreen button belongs in the same controls bar refactor.
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
  3. **Fullscreen button in controls bar** *(from BL-004)* — add a dedicated fullscreen toggle button to the player controls bar; `F` shortcut already handled by the existing keydown handler (verify it is wired correctly after BL-020 fix).
  4. **Modals usable in native fullscreen** — convert move, cut, and delete confirmation overlays to `<dialog>.showModal()` so they appear above the native fullscreen element without exiting fullscreen.
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

### BL-025 — Changer L'Icône « Aspect »

- **Dates**: `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09`

- **Why**: le bouton « aspect ratio » utilise actuellement la même icône SVG que le bouton plein écran, ce qui rend les deux actions visuellement indiscernables dans la barre de contrôles du player.
- **Expected outcome**: remplacer l'icône du bouton aspect ratio par une icône distincte qui évoque le recadrage ou le changement de ratio (ex. : deux flèches diagonales opposées avec un rectangle, ou une icône crop/fit).
- **Scope**: `frontend/index.html` — uniquement l'icône SVG inline du bouton aspect, pas de changement fonctionnel.
- **Attention point**: l'icône doit rester lisible à la taille utilisée dans la barre de contrôles (environ 20×20 px) et cohérente visuellement avec les autres icônes du player.

### BL-026 — Contrôles Plein Écran : Affichage Zone Basse + Toast Seek Systématique

- **Dates**: `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09`

- **Why**: la barre de contrôles apparaît intempestivement en plein écran — sur les sauts clavier (←/→), le survol souris (`mousemove`), et, une fois BL-024 livré, lors du scrubbing analogique au stick. Par ailleurs, le toast de seek (déjà affiché sur double-tap) est le bon feedback visuel pour toutes les actions de navigation temporelle, mais il est absent pour les touches clavier, les boutons skip et le swipe horizontal.
- **Expected outcome**:
  1. **Toast seek systématique** — `showToast()` appelé pour *toutes* les sources de seek :
     - Touches clavier ←/→ → ajouter le toast `◀◀ −Xs` / `+Xs ▶▶` (absent actuellement)
     - Swipe horizontal → afficher un toast en fin de swipe (`touchend`) avec le delta réel
     - Boutons skip (-30s, -10s, +10s, +30s) → ajouter le toast correspondant
     - Double-tap gauche/droite → déjà OK ✅
     - Gamepad D-pad et stick analogique (BL-024) → à intégrer lors de l'implémentation gamepad
  2. **Zone tactile d'affichage de la barre** — la barre se révèle uniquement si le `touchstart` / `pointerdown` se produit dans les **10 % bas de l'écran** (toute la largeur). Les taps hors de cette zone ne la révèlent pas.
  3. **Touche dédiée** — une seule touche clavier révèle/masque la barre (`H`). Les touches de seek, volume, espace et toutes les autres actions ne déclenchent plus `bumpFullscreenControlsIdle()`.
  4. **Suppression du déclencheur `mousemove`** — supprimer l'appel à `bumpFullscreenControlsIdle(true)` sur `mousemove`, ou le conditionner au survol de la zone basse uniquement.
  5. **Stick analogique** (anticipation BL-024) — le scrubbing analogique met à jour la seekbar frame par frame sans appeler `bumpFullscreenControlsIdle()`.
- **Scope**: `frontend/index.html` — `skip()`, handler `keydown`, handlers `touchend` / `touchmove`, `mousemove`, `bumpFullscreenControlsIdle()`, boutons skip.
- **Functional rules**:
  - La barre reste visible tant que l'utilisateur interagit avec la zone basse ou les contrôles ; elle se masque après `FULLSCREEN_CONTROLS_IDLE_MS` (2 200 ms) d'inactivité.
  - Le toast ne s'affiche que si une vidéo est ouverte.
  - Pour le swipe horizontal, le toast de fin de swipe affiche le delta réel (pas une valeur fixe) ; un seul toast au `touchend`, pas un par frame.
- **Attention point**: vérifier que les boutons de la barre restent cliquables après révélation (`pointer-events`), et que le hide-timer ne se réinitialise pas à chaque frame lors du scrubbing analogique.
- **Acceptance signal**: en plein écran, les sauts clavier, le swipe, les boutons skip et le scrubbing analogique ne révèlent jamais la barre de contrôles ; seul un toucher en zone basse ou la touche `H` la révèle ; un toast indiquant le montant du seek est visible pour toutes ces sources.

### BL-020 — Native Fullscreen Broken On Touch-Capable Desktop Browsers

- **Dates**: `created=2026-05-09`

- **Why**: `toggleFullscreen()` uses `navigator.maxTouchPoints > 0` as a second condition to force faux-fullscreen (CSS overlay). This was originally intended for iPad/Safari where `document.fullscreenEnabled` is already `false`. However it also fires on any touch-capable device that actually supports native fullscreen (e.g. SteamDeck running Firefox), causing native fullscreen to never be requested even though the browser supports it.
- **Expected outcome**: native fullscreen works on Firefox/SteamDeck and any other touch-capable desktop browser. iPad continues to use faux-fullscreen because `fullscreenEnabled` remains false on Safari.
- **Scope**: `toggleFullscreen()` in `frontend/index.html` — remove the `|| navigator.maxTouchPoints > 0` branch; rely solely on `!document.fullscreenEnabled`.

## Lots terminés

> Lots terminés depuis plus de 3 jours → [backlog-archive.md](backlog-archive.md)

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