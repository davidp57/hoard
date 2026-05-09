# Hoard — Backlog

## Purpose

This document is the source of truth for changes to discuss and plan outside the milestone roadmap:

- fixes discovered through testing or real usage;
- UX improvements;
- feature evolutions;
- targeted technical debt;
- follow-up items raised during user discussions.

It is intentionally lightweight, versioned in Git, and reviewed alongside the code.

Any concrete point raised by the user that needs follow-up beyond the current session should be captured here with an explicit status and updated over time.

## Working Rules

1. Add every new topic to **Inbox** with a short, concrete description.
2. Propose a **priority** (`P1`, `P2`, `P3`) before arbitration.
3. Move a topic to **Ready** once the need is clarified.
4. Move a topic to **In progress** when work starts on an active branch.
5. Move a topic to **Done** in the working branch once the pull request is ready for merge and the implementation is considered delivered in backlog terms.
6. Track ticket dates using ISO format (`YYYY-MM-DD`): `created`, `started`, `completed`.
7. Do not leave any actionable follow-up only in chat if it needs to survive beyond the current exchange.

### Priority Meaning

- `P1` — important to discuss soon; strong product impact, operational need, or notable risk.
- `P2` — useful but not blocking; improvement to schedule.
- `P3` — comfort, polish, or optional technical debt.

### Status Meaning

- `Inbox` — captured idea or need, not yet arbitrated.
- `Ready` — clarified enough to be picked up.
- `In progress` — currently being implemented on an active branch.
- `Done` — implementation delivered and PR-ready for merge.

### Date Fields

- `created` — date when the topic first entered the backlog.
- `started` — date when active implementation work began on a branch.
- `completed` — date when the ticket was considered delivered in backlog terms.
- Always use ISO format: `YYYY-MM-DD`.
- In `Subject Details`, always add a `Dates` line and include only the fields already known for the current status.
- For historical tickets created before this backlog existed, approximate `created` from the first implementation trace available in Git history.

## Proposed Priorities For The Next Discussion

1. **BL-005** — free-move destination picker in the filesystem tree.
2. **BL-002** — complete the existing file-list sorting modes.
3. **BL-003** — manual watched / unwatched toggle.

## Inbox

| ID | Created | Type | Area | Proposed Priority | Topic |
|---|---|---|---|---|---|
| BL-002 | 2026-04-12 | Improvement | File list | P2 | Complete the existing file-list sorting by adding size and watch-status modes to the current name/date controls |
| BL-003 | 2026-04-12 | Improvement | Watch state | P2 | Allow users to mark a file watched or unwatched manually from the UI |
| BL-004 | 2026-04-12 | Improvement | Player | P2 | Add a proper fullscreen button and `F` keyboard shortcut |
| BL-005 | 2026-04-12 | Improvement | File management | P1 | Add a free-move destination picker that browses the filesystem tree |
| BL-006 | 2026-04-12 | Improvement | File management | P2 | Add rename from the UI for files and folders |
| BL-007 | 2026-04-12 | Improvement | Organization | P1 | Add arbitrary tags on files and allow filtering the list by tag |
| BL-008 | 2026-04-12 | Improvement | Media | P2 | Add subtitle support by detecting `.srt` and `.ass` files in the same folder |
| BL-009 | 2026-04-12 | Improvement | Refresh | P2 | Auto-refresh the file list to detect new downloads or external filesystem changes |
| BL-010 | 2026-04-12 | Improvement | Player | P2 | Add a playback speed selector (0.5x, 1x, 1.5x, 2x) |
| BL-011 | 2026-04-12 | Security | Access | P1 | Add basic authentication for LAN-external exposure |
| BL-012 | 2026-04-12 | Improvement | Search | P3 | Add search across filenames under `MEDIA_ROOT` |
| BL-013 | 2026-04-12 | Improvement | UI | P3 | Add a light theme toggle persisted locally |
| BL-015 | 2026-04-12 | Evolution | Watch progress | P2 | Support multi-user watch progress instead of a single global progress row per file |
| BL-016 | 2026-04-12 | Improvement | Media | P3 | Display video metadata in the UI (duration, resolution, codec), likely via `ffprobe` |
| BL-020 | 2026-05-09 | Bug | Player | P1 | Native fullscreen broken on touch-capable desktop browsers (SteamDeck/Firefox): `navigator.maxTouchPoints > 0` incorrectly forces faux-fullscreen even when `document.fullscreenEnabled` is true |
| BL-021 | 2026-05-09 | Improvement | Player | P2 | Unified multi-level seek: 4 configurable durations (short/medium/long/x-long) shared across keyboard shortcuts, touch double-tap zones, and player buttons; full keyboard shortcut set for all player actions; modals usable in native fullscreen |

## Subject Details

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

## Ready

- No topic yet.

## In Progress

- No topic yet.

## Done

- **BL-020** — `created=2026-05-09`, `started=2026-05-09`, `completed=2026-05-09` — Native fullscreen now works on touch-capable desktop browsers (SteamDeck/Firefox): removed the overly-broad `navigator.maxTouchPoints > 0` condition from `toggleFullscreen()`; rely solely on `!document.fullscreenEnabled` to decide between native and faux-fullscreen. iPad/Safari unaffected because `fullscreenEnabled` is already `false` there.

- **BL-014** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Optional PWA install shell delivered with a manifest, a minimal service worker, standalone-launch polish, and explicit limits so app installability does not imply offline NAS playback.
- **BL-001** — `created=2026-04-12`, `completed=2026-04-13` — Backlog triage process considered established: ticket states, date fields, and regular backlog updates are now already part of the working workflow.
- **BL-018** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Fullscreen controls hitbox follow-up delivered: simple taps on the side zones no longer fall through to centre actions, and only a narrow bottom-centre strip can toggle controls.
- **BL-017** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Folder initial sweep UX simplified: the player now exposes a single compact action that saves the current playback position as the folder default start, without the previous inline editor.
- **BL-019** — `created=2026-04-12`, `started=2026-04-12`, `completed=2026-04-12` — Native playback investigation and first implementation delivered with a bilingual compatibility note, a new `/api/media-info` ffprobe endpoint, and player-side probing via `canPlayType()` plus `MediaCapabilities` before falling back to `/api/transcode`.
- **BL-101** — `created=2026-04-05`, `started=2026-04-05`, `completed=2026-04-06` — Web video download delivered in v2.0 with a bookmarklet, yt-dlp integration, smart source detection, server-side HTML sniffing fallback, cookie / referer passthrough, and SSRF protection.
- **BL-102** — `created=2026-04-06`, `started=2026-04-06`, `completed=2026-04-06` — Sequential download queue delivered in v2.0 with live queue modal, active badge, stop / cancel action, two-phase preparation, automatic temporary file cleanup, and download-folder auto-refresh.
- **BL-103** — `created=2026-04-06`, `started=2026-04-06`, `completed=2026-04-06` — Native HTTPS delivered in v2.0 via `SSL_CERTFILE` / `SSL_KEYFILE`, with Docker and installation documentation.