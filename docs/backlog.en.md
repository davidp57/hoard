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
5. Move a topic to **Done** only after delivery.
6. Do not leave any actionable follow-up only in chat if it needs to survive beyond the current exchange.

### Priority Meaning

- `P1` — important to discuss soon; strong product impact, operational need, or notable risk.
- `P2` — useful but not blocking; improvement to schedule.
- `P3` — comfort, polish, or optional technical debt.

### Status Meaning

- `Inbox` — captured idea or need, not yet arbitrated.
- `Ready` — clarified enough to be picked up.
- `In progress` — currently being implemented on an active branch.
- `Done` — delivered.

## Proposed Priorities For The Next Discussion

1. **BL-005** — free-move destination picker in the filesystem tree.
2. **BL-019** — investigate broader native codec playback before transcoding.
3. **BL-002** — sort controls in the file list.

## Inbox

| ID | Type | Area | Proposed Priority | Topic |
|---|---|---|---|---|
| BL-001 | Process | Product | P2 | Stabilize backlog triage and decide how this backlog is reviewed at the start of work sessions |
| BL-002 | Improvement | File list | P1 | Add sort controls in the file list: name, modified date, size, watch status |
| BL-003 | Improvement | Watch state | P2 | Allow users to mark a file watched or unwatched manually from the UI |
| BL-004 | Improvement | Player | P2 | Add a proper fullscreen button and `F` keyboard shortcut |
| BL-005 | Improvement | File management | P1 | Add a free-move destination picker that browses the filesystem tree |
| BL-006 | Improvement | File management | P2 | Add rename from the UI for files and folders |
| BL-007 | Improvement | Organization | P1 | Add arbitrary tags on files and allow filtering the list by tag |
| BL-008 | Improvement | Media | P2 | Add subtitle support by detecting `.srt` and `.ass` files in the same folder |
| BL-009 | Improvement | Refresh | P2 | Auto-refresh the file list to detect new downloads or external filesystem changes |
| BL-010 | Improvement | Player | P2 | Add a playback speed selector (0.5x, 1x, 1.5x, 2x) |
| BL-011 | Security | Access | P1 | Add basic authentication for LAN-external exposure |
| BL-012 | Improvement | Search | P3 | Add search across filenames under `MEDIA_ROOT` |
| BL-013 | Improvement | UI | P3 | Add a light theme toggle persisted locally |
| BL-014 | Improvement | Platform | P3 | Add a PWA manifest and service worker so Hoard can be installed on tablet and desktop devices |
| BL-015 | Evolution | Watch progress | P2 | Support multi-user watch progress instead of a single global progress row per file |
| BL-016 | Improvement | Media | P3 | Display video metadata in the UI (duration, resolution, codec), likely via `ffprobe` |
| BL-018 | Improvement | Player / Fullscreen | P2 | Hide player controls automatically when entering fullscreen, while preserving an obvious way to bring them back |
| BL-019 | Research | Playback / Codecs | P1 | Investigate broader native playback support across codecs and containers before transcoding, especially on iPad and other Safari-based clients |

## Subject Details

### BL-001 — Stabilize Backlog Triage

- **Why**: avoid leaving product decisions, bugs, and follow-up ideas only inside chat history.
- **Expected outcome**: a simple rule for when an item enters the backlog and how it is reprioritized.
- **Decision to make**: review cadence, expected level of detail, and when an item moves from `Inbox` to `Ready`.

### BL-002 — Sort Controls In The File List

- **Why**: browsing large raw folders becomes slower when everything is locked to the current sort behavior.
- **Expected outcome**: let users sort by name, modified date, size, and watch status, with a clear UI state.
- **Attention point**: keep the behavior simple on both desktop and touch devices.

### BL-003 — Manual Watched / Unwatched Toggle

- **Why**: users sometimes need to fix watch status manually without reopening the video.
- **Expected outcome**: allow a quick explicit action from the file list or context UI.
- **Attention point**: define whether the action resets stored playback position or only the seen threshold state.

### BL-004 — Proper Fullscreen Support

- **Why**: the current mobile overlay is useful but does not replace native fullscreen behavior in all cases.
- **Expected outcome**: add a fullscreen button and `F` shortcut with clean fallback behavior.
- **Attention point**: iPad and mobile browser limitations need explicit handling.

### BL-005 — Free-Move Destination Picker

- **Why**: predefined quick folders cover only a subset of real file-management flows.
- **Expected outcome**: browse the filesystem tree and choose any destination folder from the UI.
- **Benefit**: makes Hoard more usable as a real NAS file-management tool, not only as a player.

### BL-006 — Rename From The UI

- **Why**: file cleanup often requires quick renaming without opening SMB or another file manager.
- **Expected outcome**: rename files and folders safely from the web UI.
- **Attention point**: path safety and collision handling must stay explicit and predictable.

### BL-007 — File Tags And Tag Filtering

- **Why**: users need lightweight organization beyond watched / in-progress / watched.
- **Expected outcome**: store arbitrary tags in SQLite, display them in the list, and filter by tag.
- **Examples**: `to-finish`, `great`, `family`, `archive-later`.

### BL-008 — Subtitle Support

- **Why**: local media folders often contain sidecar subtitle files that are currently ignored.
- **Expected outcome**: detect `.srt` / `.ass` files in the same folder and expose them as selectable text tracks.
- **Attention point**: naming conventions and encoding issues need to be handled pragmatically.

### BL-009 — Auto-Refresh The File List

- **Why**: the UI currently refreshes the download folder after completed downloads, but general folder changes are still manual.
- **Expected outcome**: detect new files or external changes without requiring a full manual reload.
- **Options to discuss**: polling, SSE, or a simpler targeted refresh strategy.

### BL-010 — Playback Speed Selector

- **Why**: users increasingly expect variable playback speed in a media player.
- **Expected outcome**: expose a simple speed selector with a few useful presets.
- **Attention point**: keep the control compact enough for mobile and tablet layouts.

### BL-011 — Basic Authentication For External Exposure

- **Why**: HTTPS now exists, but exposure outside the LAN still needs an authentication layer.
- **Expected outcome**: a simple and safe authentication option for reverse-proxy or direct HTTPS deployments.
- **Attention point**: keep setup simple for self-hosted users and avoid turning the app into a full multi-account system prematurely.

### BL-012 — Search Across Filenames

- **Why**: raw filesystem browsing becomes less efficient as the media tree grows.
- **Expected outcome**: search across filenames under `MEDIA_ROOT` without introducing a metadata library.
- **Constraint**: preserve the project's philosophy of staying simple and filesystem-first.

### BL-013 — Light Theme Toggle

- **Why**: some environments and devices are easier to use with a light UI.
- **Expected outcome**: a simple theme toggle persisted locally.
- **Attention point**: keep the visual system coherent across desktop, mobile, and player states.

### BL-014 — PWA Support

- **Why**: Hoard already works well on iPad and desktop browsers; installability would reduce friction further.
- **Expected outcome**: manifest + service worker so users can install Hoard like an app on supported devices.
- **Attention point**: define how much offline behavior is actually desirable for a NAS-first application.

### BL-015 — Multi-User Watch Progress

- **Why**: a single watch-progress row per file is limiting when several people use the same Hoard instance.
- **Expected outcome**: separate watch progress by user while preserving the current lightweight architecture.
- **Attention point**: this has implications for authentication, settings, and UI complexity.

### BL-016 — Video Metadata In The UI

- **Why**: codec, duration, and resolution would help identify files before opening them.
- **Expected outcome**: display metadata in a lightweight detail pane or hover/card treatment.
- **Attention point**: any `ffprobe` usage must stay performant and avoid making folder navigation sluggish.

### BL-017 — Configurable Initial Sweep Per Folder

- **Functional rules**:
	- apply only when the file has no saved progress yet;
	- do not apply to already watched or already started videos;
	- allow `0` to mean "disabled";
	- folder override wins over the global default.
- **UX expectation**:
	- global default is configured in Settings;
	- per-folder value is editable directly from the player while a video from that folder is open;
	- the player should make it clear whether the current folder uses the global value or an override.
- **Data shape to discuss**: store a global `initial_sweep_seconds` setting plus a folder-level mapping keyed by relative folder path.
- **Attention point**: the rule should never override an existing saved position, and the folder-level configuration must stay easy to understand and edit.
- **Acceptance signal**: opening a brand-new video in a configured folder should start at the configured offset, while reopening the same video later should resume from its real saved progress instead.

### BL-018 — Hide Controls In Fullscreen

- **Why**: visible controls take too much space in fullscreen playback, especially on tablets and smaller screens.
- **Expected outcome**: hide player controls automatically in fullscreen and restore them on user interaction.
- **Attention point**: touch, mouse, and keyboard interactions need consistent behavior so controls remain discoverable and accessible.

### BL-019 — Investigate Broader Native Codec Playback

- **Why**: some devices currently fall back to transcoding, for example H.265 to H.264 on iPad, even though native playback support may exist for part of the matrix of codecs, containers, browser engines, and hardware.
- **Expected outcome**: produce a clear compatibility matrix and identify where Hoard can prefer native playback over transcoding.
- **Scope**: codec support, container support, browser differences, media source constraints, and practical detection strategy in the frontend/backend.
- **Attention point**: this should start as an investigation ticket, not as an implementation assumption.

## Ready

- No topic yet.

## In Progress

- **BL-017** — Configurable initial sweep per folder is being implemented on branch `feat/bl-017-initial-sweep`, with a global default in Settings and a per-folder override from the player UI.

## Done

- **BL-101** — Web video download delivered in v2.0 with a bookmarklet, yt-dlp integration, smart source detection, server-side HTML sniffing fallback, cookie / referer passthrough, and SSRF protection.
- **BL-102** — Sequential download queue delivered in v2.0 with live queue modal, active badge, stop / cancel action, two-phase preparation, automatic temporary file cleanup, and download-folder auto-refresh.
- **BL-103** — Native HTTPS delivered in v2.0 via `SSL_CERTFILE` / `SSL_KEYFILE`, with Docker and installation documentation.