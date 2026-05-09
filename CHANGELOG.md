# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Racine de navigation par défaut (BL-040)** : chaque home root peut être désignée comme racine par défaut (colonne `is_default` en base, endpoint `POST /api/home-roots/{id}/set-default`). L'app navigue directement vers la racine par défaut au démarrage et après validation du PIN, sans passer par l'écran de sélection. Un indicateur visuel (🏠, bordure accent, badge « défaut ») et un bouton « ⌂ » permettent de changer la racine par défaut depuis les Paramètres.
- **Contrôles manette étendus** :
  - `L1+R1+B` → supprimer le fichier courant (lecteur ou curseur browser)
  - `L1+R1+X` → déplacer le fichier courant (lecteur ou curseur browser)
  - Navigation dans les **Paramètres** : D↑/D↓ pour défiler, B ou Start pour fermer
  - Navigation dans les **dialogues** : A = confirmer (supprimer), B = annuler ; dans le dialogue de déplacement, D↑/D↓ sélectionne le dossier, A valide
  - Mise à jour de l'overlay d'aide (`Start`) avec les nouveaux raccourcis contextuel (browser, paramètres, dialogues)

### Fixed
- **Bouton « Ajouter une racine »** dans les Paramètres : le modal de navigation s'affichait derrière la page des paramètres (z-index). `openRootPicker()` ferme maintenant les paramètres avant d'ouvrir le modal.
- **Dockerfile** : correction des fins de ligne CRLF sur `entrypoint.sh` lors du build depuis Windows (`sed -i 's/\r//'`).

### Changed
- **UX « Ajouter une racine »** : le bouton n'utilise plus `currentPath` silencieusement. Il ouvre désormais la modale de navigation pour choisir le dossier, puis demande un nom (pré-rempli avec le nom du dossier sélectionné).
- **Bouton « ⌂ Dossier de départ »** dans les Paramètres : quand des home roots existent, il ouvre le sélecteur de dossier pour *ajouter* une nouvelle racine (au lieu de modifier `MEDIA_ROOT` directement). Le comportement historique (changer `MEDIA_ROOT`) est conservé si aucune home root n'est configurée.
- **`navigateHome` (bouton 🏠)** : navigue vers la racine par défaut si l'utilisateur n'y est pas déjà ; appuyer une seconde fois depuis la racine par défaut affiche l'écran de sélection multi-racines.

 Les tags sont stockés en base SQLite (`file_tags`), affichés comme badges dans la liste, et un filtre par tag apparaît dynamiquement dans la barre de tri.
- **Sélecteur de destination libre (BL-005)** : bouton « 📂 Parcourir… » dans la fenêtre de déplacement permettant de choisir n'importe quel dossier de l'arborescence comme destination.
- **Recherche dans les noms de fichiers (BL-012)** : champ de recherche dans la barre de tri ; la recherche est récursive dans le dossier courant via le nouvel endpoint `GET /api/search`.
- **Métadonnées vidéo dans l'UI (BL-016)** : codec, résolution, durée et bitrate affichés sous le titre du fichier en cours de lecture via `GET /api/media-info`.
- **Vitesse de lecture (BL-010)** : bouton de cycle de vitesse (0.5×, 1×, 1.5×, 2×) dans les contrôles du player ; la vitesse est réinitialisée à chaque ouverture de fichier.
- **Rafraîchissement automatique de la liste (BL-009)** : la liste se met à jour toutes les 30 secondes quand le navigateur est actif, l'onglet visible et la vidéo en pause.
- **Dossiers home multiples (BL-023)** : support de plusieurs racines de navigation avec gestion complète en base (`home_roots`) et interface de sélection.
- **Support manette / gamepad (BL-024)** : intégration de la Gamepad API avec boucle `requestAnimationFrame`, système 4 couches (base / L1 / R1 / L1+R1), contrôles complets du lecteur (lecture, seek, volume, plein écran, vu/non vu, déplacement rapide), navigation dans le navigateur de fichiers au gamepad, scrubbing analogique stick gauche, volume analogique stick droit, badge HUD de couche active, overlay aide (Start button), toasts de connexion/déconnexion, retour haptique Chrome, et section « 🎮 Manette » dans les Paramètres (activation, deadzone, haptique). Paramètres `gamepad_enabled`, `gamepad_deadzone`, `gamepad_haptic`, `gamepad_mapping` ajoutés au backend SQLite.

- **Configurable initial sweep for new videos**: add a global `initial_sweep_seconds` player setting plus per-folder overrides. Brand-new videos can now start at a configured offset (for example 10 minutes in), while videos with saved progress still resume from their actual saved position.
- **Playback metadata endpoint**: add `/api/media-info` backed by `ffprobe` so Hoard can inspect container, codecs, bitrate, frame rate, and audio properties before deciding how to play a file.
- **Optional PWA install shell**: Hoard now ships a web app manifest, a minimal service worker, and standalone-shell polish so supported browsers can install it as an app without changing the online-only NAS playback model.
- **4 niveaux de seek unifiés (BL-021)**: les raccourcis clavier, le double-tap et les boutons skip utilisent désormais 4 durées configurables (`seek_short`, `seek_medium`, `seek_long`, `seek_xlong`) au lieu des anciennes valeurs `doubletap_*` séparées.
- **Nouveaux raccourcis clavier (BL-021)**: navigation vidéo suivante/précédente (PageDown/PageUp), muet (M), cycle aspect ratio (A), marquer points IN/OUT (I/O), ouvrir découpe (C), ouvrir déplacement (D), supprimer (Suppr), sauvegarder position initiale (S), aide raccourcis (?).
- **Icône aspect ratio distincte (BL-025)**: le bouton Fit/Fill affiche désormais une icône SVG de cadre au lieu du symbole ⛶ qui ressemblait au bouton plein écran.
- **Toast systématique sur tous les seeks (BL-026)**: chaque seek (bouton, clavier, swipe) affiche un toast de confirmation indiquant le delta réel.
- **Modaux fullscreen compatibles (BL-021)**: les fenêtres Déplacer, Découper, Supprimer et l'aide clavier utilisent désormais les `<dialog>` HTML natifs qui restent visibles au-dessus du plein écran natif (plus de blocage par `window.confirm()`).
- **Zone de reveal des contrôles en fullscreen restreinte (BL-026)**: le déplacement de la souris ne révèle les contrôles qu'en bas de l'écran (10 %), évitant l'affichage intempestif pendant la lecture.
- **Option pour désactiver le transcodage (BL-022)**: nouveau paramètre `transcode_enabled` (défaut : activé). Quand il est désactivé, le player utilise toujours `/api/stream` sans appeler `/api/transcode`, ce qui réduit la charge CPU du NAS pour les formats supportés nativement.

### Fixed
- **Probe playback no longer transcodes too early**: formats such as HEVC-in-MP4 now keep the optimistic native `/api/stream` path even when `canPlayType()` or `MediaCapabilities` stay conservative, and only fall back to `/api/transcode` on explicit `fallback` formats or real playback failure.
- **Fullscreen controls no longer toggle from the whole video area**: the hide/show action is again limited to the intended bottom-centre zone near the controls instead of reacting to clicks across the fullscreen container.
- **Single taps on the side zones no longer trigger centre actions**: left and right fullscreen gesture areas now stay inert on single taps instead of accidentally toggling controls or play/pause.
- **Native fullscreen now works on touch-capable desktop browsers (BL-020)**: the `navigator.maxTouchPoints > 0` branch was removed from `toggleFullscreen()`. Devices such as the SteamDeck that have a touchscreen but also support `requestFullscreen()` now correctly use native fullscreen instead of the CSS faux-fullscreen overlay. iPad/Safari continues to use faux-fullscreen because `document.fullscreenEnabled` is already `false` there.

### Changed
- **Fullscreen controls now auto-hide**: entering fullscreen now hides player controls by default. On desktop they reappear on mouse movement or keyboard interaction; on touch devices they can be brought back with the existing bottom-centre controls gesture.
- **Smarter native playback selection**: the player now probes native browser support with `canPlayType()` and `MediaCapabilities` when metadata is available, and only falls back to `/api/transcode` when support is not confirmed or playback is rejected.
- **Folder initial sweep UI simplified**: the player now uses a single compact action to save the current playback position as the default start for the current folder, instead of a permanent inline editor.

## [2.0.0] - 2026-04-06

### Added
- Video download via yt-dlp: bookmarklet + 📥 button in the header let you send any web video to Hoard for download on the NAS
- `POST /api/download` endpoint: accepts a URL and optional `cookies`, `referer`, and `title` fields; creates a background job, returns a `job_id`
- **Download queue widget**: 📥 header button now shows a badge with the count of active downloads and opens a unified modal combining the add-form and a live queue list
- **Download queue modal**: lists all running/completed/failed downloads with individual progress bars; completed or failed entries can be dismissed with ✕
- **Download persistence across page reloads**: on page init the frontend reconnects to any jobs still running in the backend (downloads never stop when you close the tab)
- `DELETE /api/jobs/{job_id}` endpoint to remove a job from the in-memory store
- **Filename hint**: bookmarklet now captures `document.title` and pre-fills a "Nom du fichier" field in the modal; the value overrides yt-dlp's automatic title, giving clean filenames for embed pages
- `_sanitize_filename()` helper: strips characters invalid in filenames on Windows/Linux, caps at 180 chars
- **Server-side HTML video sniffing**: when yt-dlp reports "Unsupported URL", the backend fetches the page HTML and scans for `<video>`, `<source>`, `<iframe>`, `<meta property="og:video*">`, inline `<script>` blocks, and `data-*` attributes pointing to known video-hosting domains (BunnyCDN, YouTube embed, Vimeo, JW Platform, Brightcove, Kaltura) or direct media files (`.mp4`, `.m3u8`, `.webm`, `.mkv`) — covers JS-injected players whose URL never appears in the raw HTML. If a video source is found, yt-dlp is retried automatically.
- New settings: `download_folder` (target folder relative to `MEDIA_ROOT`, default `Downloads`) and `download_cookies_path` (path to a persistent Netscape cookies.txt file)
- Cookie passthrough: bookmarklet captures `document.cookie` and sends it with the request; a persistent cookies.txt file is also supported for authenticated sites
- Bookmarklet auto-generated in Settings → Downloads; drag-to-bookmark instructions provided
- SSRF protection on `/api/download`: `file://`, localhost, and RFC-1918 private network addresses are rejected
- **Smart video source detection**: bookmarklet captures `<video>.currentSrc` from the page DOM — 6 strategies including iframe detection for BunnyCDN / YouTube / Vimeo embeds
- Referer header passthrough: when downloading a direct video URL, the original page URL is sent as `Referer`

- **Native HTTPS support**: set `SSL_CERTFILE` and `SSL_KEYFILE` environment variables to serve Hoard over HTTPS without a reverse proxy. Commented instructions in `docker-compose.yml` show how to mount a cert folder and enable it. Generate a self-signed cert with `openssl req -x509 -newkey rsa:4096 ...` or a locally-trusted cert with `mkcert`.
- **Sequential download queue**: downloads are now processed one at a time — new jobs wait in a `pending` state until the current download finishes, preventing bandwidth overload.
- **Stop button on downloads**: each pending or running download now shows a ⏹ stop button in the queue modal; clicking it cancels the job immediately (pending) or aborts the active yt-dlp transfer (running). Partial `.part` files left by yt-dlp are deleted automatically on cancellation.
- **Auto-refresh download folder**: when a download completes, the file browser automatically refreshes if the user is currently browsing the download folder.
- **Two-phase download preparation**: when a job is submitted (via bookmarklet or UI), a dedicated thread immediately runs phase 1 — sets a filename preview from the page title and transitions the job `pending` → `resolving` → `pending` — before placing it in the queue. The bookmarklet toast now shows ⌛ "Analyse de l'URL…" right away, then ⏳ "En attente — titre.mp4" while waiting, instead of being stuck on the initial connection state.
- **Bookmarklet queue awareness**: the bookmarklet status dialog now correctly distinguishes ⏳ "En attente dans la file…" (queued, not yet started) from ⌛ "Analyse de l'URL…" (running), and shows ⏹ "Annulé" if the job is cancelled from the Hoard UI.

### Fixed
- Cloudflare anti-bot 403 errors: yt-dlp now impersonates Chrome via `curl-cffi` (`impersonate` option at top-level, `curl-cffi>=0.10.0,<0.15.0`)
- Invalid Netscape cookie file format: domain is now prefixed with `.` as required when `include_subdomains=TRUE`
- Bookmarklet/PIN flow: after entering the PIN the download queue modal no longer opened — two call sites of `openDownloadModal` had not been renamed to `openDlQueueModal`
- Bookmarklet: submits the download directly to Hoard in the background via `fetch()` — no page navigation, no modal — a status dialog injected into the current page shows live progress: "Connexion à Hoard…" → "Analyse de l'URL…" → "Téléchargement… X%" → "Terminé !" (auto-close) or "❌ error" (manual close). The `#download?` hash redirect is kept for backward compatibility.

## [1.0.0] - 2026-04-05

### Added
- Settings page with PIN lock (numeric, SHA-256 hashed), accessible via ⚙️ button in header
- Configurable touch gestures: enable/disable per category, edge zone %, swipe threshold, sensitivity, double-tap values
- Configurable privacy timeout (auto-close player after N minutes of inactivity)
- Configurable watched threshold (default 90%)
- Home folder and sort order are stored in backend DB (migrated from localStorage)
- Multi-tap seek accumulation: N taps = (N−1) × base seek value
- 3 vertical zones on both left and right seek edges (top=fastest, bottom=slowest)
- Fit/Fill toolbar button (replaces triple-tap gesture)
- Full bilingual documentation (EN + FR): user guide, installation, developer guide, getting-started guide
- Page Visibility API privacy: player auto-closes when device wakes after timeout
- Seek bar touch area extended (±20px) to prevent swipe conflict
- Double-tap right zone split into 3 vertical thirds (+30s / +60s / +90s base values)

### Changed
- Project renamed from MediaBrowser to Hoard
- Docker image: `ghcr.io/davidp57/nas-vid-bro` → `ghcr.io/davidp57/hoard`
- docker-compose service name: `mediabrowser` → `hoard`
- README rewritten as bilingual entry point

[Unreleased]: https://github.com/davidp57/hoard/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/davidp57/hoard/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/davidp57/hoard/releases/tag/v1.0.0
