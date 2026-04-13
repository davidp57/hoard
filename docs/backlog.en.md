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

1. **BL-017** — simplify the folder initial-sweep UX to a single in-player action.
2. **BL-018** — fix the fullscreen controls hitbox regression.
3. **BL-005** — free-move destination picker in the filesystem tree.

## Inbox

| ID | Created | Type | Area | Proposed Priority | Topic |
|---|---|---|---|---|---|
| BL-001 | 2026-04-12 | Process | Product | P2 | Stabilize backlog triage and decide how this backlog is reviewed at the start of work sessions |
| BL-002 | 2026-04-12 | Improvement | File list | P1 | Add sort controls in the file list: name, modified date, size, watch status |
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
| BL-014 | 2026-04-12 | Improvement | Platform | P3 | Add a PWA manifest and service worker so Hoard can be installed on tablet and desktop devices |
| BL-015 | 2026-04-12 | Evolution | Watch progress | P2 | Support multi-user watch progress instead of a single global progress row per file |
| BL-016 | 2026-04-12 | Improvement | Media | P3 | Display video metadata in the UI (duration, resolution, codec), likely via `ffprobe` |

## Subject Details

### BL-001 — Stabilize Backlog Triage

- **Dates**: `created=2026-04-12`

- **Why**: avoid leaving product decisions, bugs, and follow-up ideas only inside chat history.
- **Expected outcome**: a simple rule for when an item enters the backlog and how it is reprioritized.
- **Decision to make**: review cadence, expected level of detail, and when an item moves from `Inbox` to `Ready`.

### BL-002 — Sort Controls In The File List

- **Dates**: `created=2026-04-12`

- **Why**: browsing large raw folders becomes slower when everything is locked to the current sort behavior.
- **Expected outcome**: let users sort by name, modified date, size, and watch status, with a clear UI state.
- **Attention point**: keep the behavior simple on both desktop and touch devices.

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

- **Dates**: `created=2026-04-12`

- **Why**: Hoard already works well on iPad and desktop browsers; installability would reduce friction further.
- **Expected outcome**: manifest + service worker so users can install Hoard like an app on supported devices.
- **Attention point**: define how much offline behavior is actually desirable for a NAS-first application.

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

- **Dates**: `created=2026-04-12`, `started=2026-04-13`

- **Why**: visible controls take too much space in fullscreen playback, especially on tablets and smaller screens.
- **Expected outcome**: keep fullscreen auto-hide, but restrict the hide/show tap or click behavior to the intended bottom-centre zone near the controls.
- **Attention point**: user interaction outside that bottom-centre zone must not trigger hide/show side effects, otherwise normal clicks and taps become disruptive.
- **Reopened because**: the first implementation introduced a hitbox regression where hide/show behavior is triggered too broadly across the fullscreen video area.
- **Acceptance signal**: in fullscreen, clicking or tapping outside the bottom-centre control zone does not toggle the controls, while the intended bottom-centre area still does.

### BL-019 — Investigate Broader Native Codec Playback

- **Dates**: `created=2026-04-12`, `started=2026-04-12`, `completed=2026-04-12`

- **Why**: some devices currently fall back to transcoding, for example H.265 to H.264 on iPad, even though native playback support may exist for part of the matrix of codecs, containers, browser engines, and hardware.
- **Expected outcome**: produce a clear compatibility matrix and ship a first metadata-driven decision path so Hoard can prefer native playback over transcoding when browser support is actually confirmed.
- **Scope**: codec support, container support, browser differences, media source constraints, an on-demand metadata endpoint, and practical detection strategy in the frontend/backend.
- **Attention point**: keep `/api/transcode` as the safety net even after browser-side probing is added.

## Ready

- No topic yet.

## In Progress

- **BL-018** — Fix the fullscreen controls hitbox so hide/show is only triggered from the intended bottom-centre zone near the controls.

## Done

- **BL-017** — `created=2026-04-12`, `started=2026-04-13`, `completed=2026-04-13` — Folder initial sweep UX simplified: the player now exposes a single compact action that saves the current playback position as the folder default start, without the previous inline editor.
- **BL-019** — `created=2026-04-12`, `started=2026-04-12`, `completed=2026-04-12` — Native playback investigation and first implementation delivered with a bilingual compatibility note, a new `/api/media-info` ffprobe endpoint, and player-side probing via `canPlayType()` plus `MediaCapabilities` before falling back to `/api/transcode`.
- **BL-101** — `created=2026-04-05`, `started=2026-04-05`, `completed=2026-04-06` — Web video download delivered in v2.0 with a bookmarklet, yt-dlp integration, smart source detection, server-side HTML sniffing fallback, cookie / referer passthrough, and SSRF protection.
- **BL-102** — `created=2026-04-06`, `started=2026-04-06`, `completed=2026-04-06` — Sequential download queue delivered in v2.0 with live queue modal, active badge, stop / cancel action, two-phase preparation, automatic temporary file cleanup, and download-folder auto-refresh.
- **BL-103** — `created=2026-04-06`, `started=2026-04-06`, `completed=2026-04-06` — Native HTTPS delivered in v2.0 via `SSL_CERTFILE` / `SSL_KEYFILE`, with Docker and installation documentation.