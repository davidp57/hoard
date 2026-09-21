# Roadmap — Hoard

## Session cookie and bookmarklet token *(done, target version to be agreed)*

HTTP Basic auth went live in production on 2026-09-21. It protects correctly and
cost two things: credentials retyped in every new browser window, through the
browser's native dialog — barely steerable with a gamepad on the Deck and the
Frame — and a **broken bookmarklet**, since a cross-origin POST carries no Basic
credentials. Two deliberately distinct mechanisms, because one cannot fix the
other: a correct session cookie is `SameSite=Lax`, which is precisely what stops a
third-party page from acting on your behalf. See lot
[SEC-SESSION](.backlog/SEC-SESSION/PRD.md).

- [x] **Login screen and signed session cookie** (BL-123) — 30 days, slid on use;
      `WWW-Authenticate` withheld from browsers, kept for `curl -u`; Basic still
      accepted
- [x] **Dedicated token for the bookmarklet** (BL-124) — in the request body,
      never in a URL; opens the two download routes and nothing else

Reproducing BL-124 corrected the diagnosis: the CORS **preflight** was refused
first, by the auth middleware sitting outside `CORSMiddleware`, so the real POST
was never sent and the bookmarklet blamed the site's CSP for an authentication
failure.

Out of scope and argued in the PRD: logging out as a feature (the route exists,
the UI does not advertise it), and tightening `allow_origins=["*"]`.

## VR 180° side-by-side in the web player *(done, target version to be agreed)*

180° stereoscopic side-by-side files opened as ordinary video — two squashed
pictures, unwatchable. The web player now deprojects the hemisphere onto a WebGL
canvas laid over the `<video>`, which keeps driving playback and progress. Two
outputs: a flat view to pan on a normal screen, and a side-by-side output for XR
glasses in 3D mode (Steam Deck + Viture Beast). See lot
[FEAT-VR180](.backlog/FEAT-VR180/PRD.md).

- [x] **Deprojection, flat view and look controls** (BL-119) — the gate ticket
- [x] **Side-by-side output** for XR glasses (BL-120)
- [x] **VR file detection and per-file memory** (BL-121)
- [x] **Settings**: field of view, convergence, look speed, sbs layout (BL-122)

The Deck-and-glasses check was done on 2026-09-21 and found two usability
defects, fixed by lot [FIX-XR-DISPLAY](.backlog/FIX-XR-DISPLAY/PRD.md):

- [x] **Pad windows at the screen's scale** (BL-126) — the Select menu kept a
      fixed 380px width, and the button map was an SVG drawing that never grew,
      so its callouts rendered at 5.7px whatever the resolution. The drawing is
      now a text list flowing into columns.
- [x] **Guess the side-by-side layout** (BL-125) — 3840×1080, the output those
      glasses need for 3D, is full-SBS, while the setting defaulted to `half`
      and so halved the vertical field of view. The layout is now deduced from
      the canvas shape; an explicit choice still wins, and **L2** toggles it on
      the pad, **B** on the keyboard.

Verified on the hardware the same day: the Select menu reads `auto : non
étirée`, so the guess picks `full` on its own and that is the right one on the
Beast. That test in turn surfaced two gaps — about driving rather than about the
picture — covered by lot [PAD-VR](.backlog/PAD-VR/PRD.md):

- [x] **Readable pad windows in side-by-side** (BL-127) — the Select menu and the
      button map were drawn once, centred, so they straddled the split and each
      eye got half of them. Now drawn once per eye, like the toast.
- [x] **A VR layer under R2** (BL-128) — zoom, convergence and the two recentres,
      adjustable while watching the picture change instead of through a menu that
      covers it. Convergence had no pad shortcut at all, and the field of view
      only had the mouse wheel.
- [x] **Per-file convergence** (BL-129) — the strain comes from how a file was
      shot, so it is remembered per file rather than globally.

This does not reopen [ADR 0003](docs/adr/0003-client-natif.md): an immersive
OpenXR session for the Steam Frame stays out of scope and unverifiable until the
headset ships. What the ADR ruled out was a stereo OpenXR renderer, not a
deprojection in the browser — and the Deck-plus-glasses half of the need is met
by a plain side-by-side picture, with no OpenXR at all.

## v3.0 — Native client *(in progress)*

Native Flutter client talking to the existing HTTP API, targeting Steam Deck
(x86_64), Steam Frame (ARM64) and the Windows touch laptop. Playback uses
libmpv via `media_kit`, reading raw files from `/api/file` — no server-side
transcoding. See [ADR 0003](docs/adr/0003-client-natif.md) and lot
[CLIENT-NATIVE](.backlog/CLIENT-NATIVE/PRD.md).

- [x] **Feasibility spike** (BL-104) — measured on a real Steam Deck
- [ ] **Renderer decision** (BL-109) — the pivotal ticket, see below
- [ ] **Full UI parity** with the web frontend (BL-107, BL-108, BL-110..115)
- [ ] **Packaging**: Flatpak x86_64 then ARM64, Windows build, CI (BL-116, BL-117)

What the spike changed. The keyboard fault that motivated the lot was
**Edge-only**: Steam+X works in a native app, so the built-in keyboard drops to
a comfort feature. Hardware decoding engages (`auto-safe` → `vaapi-copy`, 102%
of one core against 118% in software); forcing `vaapi` is counterproductive.
The actual blocker is that **`media_kit` never tells Flutter a new frame
landed** — 8 fps at rest, 25 as soon as any animation runs. That does not
question Flutter, it questions the video brick, and BL-109 must settle it by
measurement.

The web frontend stays maintained — it serves the iPad and any browser.
Immersive VR playback (SBS 180°/360°) is explicitly **out of scope**: it needs
OpenXR stereo rendering and will be a separate application.

## v2.6.5 — An open instance must be visible *(done)*

HTTP Basic auth (BL-011) was correct but switched itself off in silence when
its env vars were unset, so a publicly reachable instance logged exactly like a
protected one. Startup now states the auth state and names what "disabled"
means; `docker-compose.yml` and the installation docs carry the warning. A new
public `/healthz` route fixes the container health check, which hit a protected
route with no credentials and marked every authenticated deployment unhealthy.
See lot [SEC-AUTH](.backlog/SEC-AUTH/PRD.md).

- [x] **Health probe surviving auth** (BL-105)
- [x] **Auth state announced at startup, in compose and in the docs** (BL-106)

## v1.0 — Initial release *(done)*

- [x] Filesystem browser with breadcrumb navigation
- [x] Integrated HTML5 video player with seek bar and controls
- [x] Auto-save playback position every 5 s; resume at last position on re-open
- [x] Visual status in file list: unseen / in-progress (% + bar) / watched (≥ 90 %)
- [x] Move file to predefined folder (quick modal) + delete with confirmation
- [x] Touch gestures: swipe-seek (3 vertical speed zones), swipe-volume, multi-tap seek, tap = play/pause
- [x] Keyboard shortcuts: Space, ←→ seek, ↑↓ volume
- [x] Responsive: split-view on desktop, faux-fullscreen overlay on mobile/iOS
- [x] On-the-fly H.265 → H.264 transcoding with auto-fallback
- [x] Settings page: home folder, sort order, watched threshold, privacy timeout
- [x] PIN lock (numeric, SHA-256 hashed) with configurable timeout
- [x] Fully configurable touch gestures (enable/disable per category, sensitivity, zones)
- [x] Fit/Fill toggle button in player toolbar
- [x] Page Visibility API privacy: auto-close player after configurable inactivity timeout
- [x] Full bilingual documentation (EN + FR): user guide, installation, developer and getting-started guides
- [x] Docker + docker-compose for Synology deployment (ghcr.io image)

## v2.0 — Web Download *(done)*

- [x] Video download via yt-dlp: bookmarklet + 📥 button in the header
- [x] Background bookmarklet: submits download via `fetch()`, shows live status dialog on the current page (no navigation)
- [x] Smart video source detection: captures `<video>.currentSrc`, iframe detection (BunnyCDN / YouTube / Vimeo), 6 capture strategies
- [x] Server-side HTML sniffing fallback: scans `<video>`, `<source>`, `<iframe>`, `<meta og:video>`, inline `<script>`, `data-*` — retries yt-dlp automatically if a source is found
- [x] Download queue widget: 📥 badge, live modal with progress bars, dismiss completed jobs
- [x] Sequential queue: one download at a time via `queue.Queue`, stop/cancel button, automatic `.part` file cleanup on cancel
- [x] Auto-refresh file browser when a download completes
- [x] Cookie passthrough (bookmarklet + persistent `cookies.txt`), Referer passthrough
- [x] HTTPS support: native via `SSL_CERTFILE` / `SSL_KEYFILE` env vars (no reverse proxy needed)
- [x] SSRF protection on `/api/download` (rejects `file://`, localhost, RFC-1918)

## v1.2 — Player & Sort *(done)*

- [x] **Unified multi-level seek** (BL-021): 4 configurable seek durations (short/medium/long/x-long) shared by keyboard shortcuts, touch double-tap zones, and player buttons; extended keyboard shortcut set (M, A, I, O, C, D, Delete, S, PageDown/PageUp, ?); move/cut/delete modals usable in native fullscreen via `<dialog>.showModal()`
- [ ] **Sort controls** in file list: by name (asc/desc), date modified, size, watch status (BL-002)
- [x] **Fullscreen button** on player + `F` shortcut (BL-021)
- [x] **Playback speed** selector (0.5×, 1×, 1.5×, 2×) (BL-010)
- [ ] Mark file as watched / unwatched manually (right-click / long-press) (BL-003)

## v1.3 — Navigation & Tags *(done)*

- [x] **Multiple home roots**: configure named root folders so the home screen lists several roots (BL-023)
- [x] **Free-move**: destination picker that browses the filesystem (folder tree) (BL-005)
- [x] **Arbitrary tags** on files (e.g. "excellent", "à finir") — stored in SQLite, shown as badges in the list (BL-007)
- [x] **Filter list by tag** — tag filter bar appears dynamically in the sort bar (BL-007)
- [x] **Search across filenames** — recursive search field in the sort bar, scoped to the current folder (BL-012)
- [ ] **Rename** file/folder inline (BL-006)

## v1.4 — Media & Subtitles

- [ ] **Subtitle support**: auto-detect `.srt` / `.ass` files in the same folder and offer them as text tracks (BL-008)
- [x] **Auto-refresh** file list every 30 s when the tab is active and video is paused (BL-009)
- [x] Display video metadata under the player title (duration, resolution, codec, bitrate) via `ffprobe` (BL-016)

## v2.1 — Multi-Segments & Gamepad Polish *(done)*

- [x] **Multi-segment export** (BL-047–051): replace single IN/OUT cut with multi-segment system; segments stored in SQLite; export individual or merged via FFmpeg lossless concat; full keyboard and gamepad support (`I`/`O`/`E`, `L1+Y`/`R1+Y`/`L1+R1+Y`)
- [x] **Auto-play next in fullscreen**: after delete/move/cut of the current file in fullscreen, the next file starts automatically and fullscreen is restored
- [x] **Volume OSD**: on-screen volume bar with icon, level, and percentage; auto-hides after 2.5 s
- [x] **Fullscreen progress indicator**: zoomed progress bar overlay in native fullscreen (time remaining, global bar, zoomed segment)
- [x] **Gamepad fullscreen dialogs** (BL-046): delete and move dialogs visible and navigable in native fullscreen on SteamDeck/Edge
- [x] **Gamepad cursor preservation** (BL-043/052): cursor no longer resets after file actions or auto-play next
- [x] **Default home root** (BL-040): designate a root as the startup destination; navigate there directly without the root-picker screen

## v2.3 — Security, Quality & UX *(done)*

- [x] **Optional HTTP Basic auth** (BL-011): enable via `HOARD_AUTH_USER` / `HOARD_AUTH_PASS`, disabled by default
- [x] **Hardened PIN hashing** (BL-030): scrypt with per-PIN salt; transparent migration from legacy SHA-256
- [x] **HTTP security headers** (BL-029): `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, CSP
- [x] **Audit logging** (BL-036): INFO trail for delete/move/download/settings + client IP, WARNING on failed PIN
- [x] **Robustness**: `MEDIA_ROOT` thread-safety (BL-032), DB-first delete/move atomicity (BL-034), job-store TTL purge (BL-033), progress-map covering index (BL-035), cookies-path validation (BL-031)
- [x] **Frontend**: fetch timeout + network feedback (BL-037), accessibility pass (BL-039), touch gesture discovery overlay (BL-038), keyboard-help contrast fix (BL-065)

## v2.3 — Player desktop UX polish *(done)*

- [x] **Windowed fullscreen by default on desktop** (BL-066): `F` = in-window immersive fullscreen, `Shift+F` = real OS fullscreen; touch devices keep the real API
- [x] **Escape goes up one level** (BL-068): keyboard navigation mirrors the gamepad (Esc = B / `nav_back`), shared `navigateUp()`
- [x] **Remove dead `/api/stream` endpoint** (BL-067): playback fully consolidated on `/api/file`

## v2.0 — Platform

- [x] **Basic authentication** delivered as optional HTTP Basic auth (BL-011) — see v2.3
- [ ] **Light theme** toggle (persisted in localStorage)
- [ ] **PWA** manifest + service-worker: installable on iPad / Windows laptop
- [ ] **Search** across all filenames in MEDIA_ROOT
- [ ] **Multi-user** watch progress (per-user SQLite rows)

## v1.5 — Gamepad / Controller Support *(done)*

- [x] **Gamepad support** (BL-024): Gamepad API, 4-layer button system (base / L1 / R1 / L1+R1), full player controls (play/pause, seek multi-level, volume, fullscreen, watched toggle, aspect ratio, quick-folder moves), file browser cursor navigation, analog left-stick scrubbing, analog right-stick volume, layer HUD badge, dynamic button-map overlay (Start), connection/disconnection toasts, haptic feedback (Chrome), configurable deadzone and on/off toggle in Settings

## v1.7 — Alternative Media Readers *(planned)*

- [ ] **Image viewer** (BL-053+054): browse folders of images with keyboard/gamepad, two display modes (page-width / full-page)
- [ ] **Archive reader** (BL-055): open `.zip`, `.cbz`, `.cbr` comic archives directly in the image viewer
- [ ] **PDF reader** (BL-056): PDF.js-powered reader with page navigation, zoom, keyboard/gamepad control, and saved progress
- [ ] **Audio player** (BL-057): native audio playback for `.mp3`, `.flac`, `.ogg`, `.m4a`, `.aac`, `.wav`, `.opus` using existing player infrastructure

## v2.6.4 — Moving onto a taken destination *(done)*

- [x] **A taken destination crashed the move job** (BL-090): `_run_move` rewrote the progress row's path onto the destination without checking one was already there — `progress.path` is a PRIMARY KEY. The `IntegrityError` went up an unguarded job thread, so the job stayed `running` for ever and the UI waited on a move that never came. The crash was in fact an accidental guard: nothing checked the destination was free, and on Linux `shutil.move()` goes through `os.rename()`, which clobbers in silence. The endpoint now refuses with a **409** carrying what the client needs to ask, and the UI offers **Overwrite / Cancel** — pad cursor starting on Cancel, since overwriting cannot be undone. The replaced file is set aside and only deleted once the move lands
- [x] **A moved folder lost its contents' metadata** (BL-091): the move rewrote its own path only, while rename already migrated descendants. `file_tags` was migrated nowhere and purged nowhere — tags were lost on both move and rename, and deleting a folder left every row below it behind
- [x] **A failed move job now reports itself** (BL-092): the job body is guarded, so a failure surfaces as an errored job instead of a spinner that never resolves
- [x] **The generic pad cursor was invisible** (BL-093): BL-088 gave every unspecialised dialog a roving focus, but the `gp-cursor` class it sets was only styled on `.entry`, `.modal-folder-btn` and three named buttons — in the eight other dialogs the cursor moved with nothing to show for it

## v2.6.2 — Everything reachable from the pad *(done)*

- [x] **Pad context menu** (BL-086): the sort bar, the row actions and half the header had no pad path at all — the sort had no keyboard path either. **Select** now opens a menu listing what applies where the user stands, in two sections: the entry under the cursor, and the current folder. Select rather than LB/RB, which never fire an action — the polling loop skips them as pure modifiers — and which was a duplicate of Start in the browser anyway
- [x] **Mark watched without opening the file** (BL-003, pending since v1.2): a new explicit `watched` column wins over the position percentage, because a file that was never opened has no duration to express the state with
- [x] **The pad passed through six dialogs out of nine** (BL-088): tags, rename, new folder, browse, destination picker and download queue are plain divs the modal detection ignored, so the pad kept driving the list behind them. Membership now lives on the overlay itself, and any unspecialised dialog gets a generic roving focus — the PIN screen gains pad-driven entry for free
- [x] **Context menu in the player** (BL-089): the player was the last place where Select meant something else, and the folder start position the last button in the app with no pad path. L2 and R2 are in fact free everywhere — no layer, no context, no read of `buttons[6]`/`buttons[7]` — but the button map draws neither, so an action mapped there would have been undiscoverable; the menu needs no redrawing and makes the rule uniform: Select opens the menu, everywhere
- [x] **Four inert buttons in the browser** (BL-087): X, Y, L3 and R3 fell back on player actions that test `hasVideo` first and did nothing. The browser layer is declared explicitly now, and Start gives back the button map

## v2.6.1 — Sort by last watched *(done)*

- [x] **Sort by last watched** (BL-085): the "Date" sort orders by filesystem `mtime`, which cannot answer "what did I watch last" — playing a media writes nothing to disk, and a folder's `mtime` never picks up a change from the depth below it. A watched video two levels down left its top folder in 14th place. A fifth criterion, **Vu**, now orders by `progress.updated_at`, a column stored since day one and never read: every folder inherits the date of the most recent media found anywhere below it. Never-watched entries group at the end of the list whatever the direction. "Date" keeps its own meaning — what just arrived in this folder

## v2.6 — Retry from history *(done)*

- [x] **Relaunch a download from its history entry** (BL-084): a ↻ button on every row queues the same URL again, carrying over the title and the Referer (now persisted — without it a direct CDN URL is rejected on origin checks). A successful entry asks for confirmation first, since the retry produces a second file suffixed `(2)`. Cookies are deliberately not stored, so authenticated sites rely on the persistent cookies.txt setting

## v2.5.2 — Destination picker follow-up *(done)*

- [x] **Tests reached the real yt-dlp** (BL-083): download threads outliving their test imported the genuine module and issued a real, timeout-less HTTP request — the suite stalled locally one run in two, and CI's "Run tests" step hung until the 6-hour limit (blamed on faulty runners across three releases). A session fixture now makes the real module unreachable, and production passes a `socket_timeout` so a silent server cannot pin the sequential queue
- [x] **The "Parcourir…" button did nothing** (BL-082): the folder picker opened *behind* the settings page (`z-index` 300 vs 500), and would have opened empty anyway — `_loadDestPickerDir()` parsed a 404 body as success and then threw on `r.entries`, leaving neither list nor message. Both fixed; the file-move picker gains the same guard

## v2.5.1 — Download integrity *(done)*

- [x] **No more silent losses** (BL-079): yt-dlp skips a download whose target name is taken, raises nothing and still emits `finished` — Hoard reported it as done for a file it never wrote. Output names are now made unique up front, a skip is detected and surfaced as an error, and no job reaches `done` without the file being on disk
- [x] **Visible destination** (BL-080): the download folder is created on demand, so a mistyped setting silently sent everything to a folder nobody could locate. The full resolved path is now shown, a warning flags a folder that does not exist yet, and it can be picked by browsing
- [x] **Restart test can no longer kill the test runner** (BL-081): session-wide backstop plus a race-free patch point

## v2.5 — Traceability & Operations *(done)*

- [x] **Download history** (BL-075): persist download jobs in SQLite (table `downloads`), history view in the 📥 modal with final status and error message, unlimited retention by default, jobs interrupted by a restart marked as such
- [x] **Log retention** (BL-076): daily-rotating log file on the persistent volume, 30 days kept (`LOG_DIR` / `LOG_RETENTION_DAYS`), log viewer in Settings → Maintenance
- [x] **Restart from the UI** (BL-077): `POST /api/restart` + button in Settings → Maintenance, guarded against active downloads, auto-reload once the backend answers again
- [x] **Download worker resilience** (BL-078): an unexpected exception used to kill the `dl-worker` thread permanently, leaving every later download stuck in `pending` with no error surfaced anywhere

---

> Items within each milestone are roughly ordered by priority.
> The roadmap is intentionally kept small — complexity is the enemy here.
