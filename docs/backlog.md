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
| Lot 2 — BL-024 Gamepad | 70 min | ~90 min | 1.29 | 15 min | ~15 min | facteur inchangé (0,40) : dépassement lié au review Copilot (7 corrections) |
| Lot 2 — BL-024 Gamepad | 70 min | ~90 min | 1.29 | 15 min | ~15 min | facteur inchangé (0,40) : dépassement lié au review Copilot (+7 fixes), pas à la complexité initiale |

> - Tickets de finition / tests simples → estimation de référence 3–5 min, pas 10–20 min.
> - Avant d'estimer un ticket de « review fix », vérifier si le problème existe réellement.
> - Pour les tickets d'implémentation technique pure, appliquer un facteur **0,60** par rapport à l'estimation initiale naïve.

---

## Lots actifs

### Lot 5 — Fonctionnalités avancées (~110 min : 95 min Copilot + 15 min gestion)

> Dépendance interne : BL-015 dépend de BL-011 (progression multi-utilisateur présuppose une couche d'authentification) — BL-011 est dans le Lot 6 (sécurité) et doit être livré en premier.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-002 | Tri dans la liste : taille + état de lecture | P2 | 10 min | 2026-04-12 | | |
| BL-003 | Marquer manuellement vu / non vu | P2 | 10 min | 2026-04-12 | | |
| BL-006 | Renommage de fichiers/dossiers depuis l'UI | P2 | 15 min | 2026-04-12 | | |
| BL-008 | Sous-titres (`.srt` / `.ass` dans le même dossier) | P2 | 25 min | 2026-04-12 | | |
| BL-013 | Thème clair (toggle) | P3 | 20 min | 2026-04-12 | | |
| BL-015 | Progression de lecture multi-utilisateur *(dépend de BL-011)* | P2 | 35 min | 2026-04-12 | | |

---

### Lot 6 — Sécurité, Qualité & UX (~175 min : 160 min Copilot + 15 min gestion)

> Issu de la revue technique complète du 2026-05-09. Tickets ordonnés par criticité descendante.
> BL-011 est le prérequis de BL-015 (Lot 5) — livrer ce lot avant le Lot 5.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-011 | Authentification basique pour exposition hors LAN | P1 | 20 min | 2026-04-12 | | |
| BL-027 | Streaming — validation Range header (HTTP 416) | P1 | 5 min | 2026-05-09 | | |
| BL-028 | safe_path() — bloquer les symlinks dans rglob/iterdir | P1 | 10 min | 2026-05-09 | | |
| BL-029 | Security headers HTTP (X-Content-Type-Options, X-Frame-Options) | P1 | 5 min | 2026-05-09 | | |
| BL-030 | PIN — remplacer SHA-256 sans sel par scrypt | P1 | 10 min | 2026-05-09 | | |
| BL-031 | download_cookies_path — valider et restreindre le chemin | P1 | 5 min | 2026-05-09 | | |
| BL-032 | MEDIA_ROOT global — thread-safety (threading.Lock) | P2 | 10 min | 2026-05-09 | | |
| BL-033 | _jobs — purge TTL des jobs terminés (fuite mémoire) | P2 | 10 min | 2026-05-09 | | |
| BL-034 | delete/move — inverser ordre FS+DB pour atomicité | P2 | 10 min | 2026-05-09 | | |
| BL-035 | init_db() — index sur progress.path | P2 | 5 min | 2026-05-09 | | |
| BL-036 | Logging — audit trail des opérations sur fichiers | P2 | 20 min | 2026-05-09 | | |
| BL-037 | Frontend — timeout fetch + feedback réseau (AbortController) | P2 | 10 min | 2026-05-09 | | |
| BL-038 | Gestes tactiles — overlay découverte au premier lancement | P3 | 15 min | 2026-05-09 | | |
| BL-039 | Accessibilité — aria-label, :focus-visible, contraste text-dim | P3 | 20 min | 2026-05-09 | | |

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

---

## Lots terminés

> Lots terminés depuis plus de 3 jours → [backlog-archive.md](backlog-archive.md)

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

---

### BL-027 — Streaming Range Header Validation

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — critique.
- **Why**: the Range header parser in `/api/stream` does not validate that `start <= end` or that values are within file bounds. An inverted or out-of-bounds range can cause a 500 or unexpected behavior. Multi-range requests (`bytes=0-100,200-300`) are not handled and crash the parser.
- **Expected outcome**: return HTTP 416 (Range Not Satisfiable) for any malformed, inverted, or out-of-bounds range; ignore unsupported multi-range syntax gracefully.
- **Attention point**: must not break normal browser seeks or partial content responses.

---

### BL-028 — safe_path() Symlink Escape Fix

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — critique.
- **Why**: `folder.rglob("*")` and `folder.iterdir()` follow symlinks by default. A symlink inside `MEDIA_ROOT` pointing to `/etc` passes `safe_path()` (which only checks the root) and exposes system files in directory listings.
- **Expected outcome**: for every item discovered by rglob/iterdir, skip symlinks or verify `item.resolve().is_relative_to(MEDIA_ROOT)` before including it in any response or operation.
- **Attention point**: must not break legitimate directory traversal for real nested folders.

---

### BL-029 — Security HTTP Headers Middleware

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — critique.
- **Why**: no security headers are set. Missing `X-Content-Type-Options: nosniff` enables MIME-sniffing attacks; missing `X-Frame-Options: DENY` allows clickjacking; missing `Content-Security-Policy` reduces defense-in-depth.
- **Expected outcome**: add a `BaseHTTPMiddleware` that injects at minimum `X-Content-Type-Options`, `X-Frame-Options`, and a minimal CSP (`default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'`) on every response.
- **Attention point**: CSP must not break the single-file inline CSS/JS frontend; `unsafe-inline` is acceptable given the architecture.

---

### BL-030 — PIN Hashing: SHA-256 → scrypt

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: PIN is currently hashed with `hashlib.sha256` with no salt. A 4-digit PIN has only 10 000 possibilities; a rainbow table cracks it instantly. A slow KDF is required for any credential storage.
- **Expected outcome**: replace with `hashlib.scrypt` (stdlib, no new dependency) with a random salt stored alongside the hash in the `settings` table. Existing stored PINs must be migrated gracefully (force re-entry on first login after upgrade).
- **Attention point**: scrypt parameters (N, r, p) must be tuned to balance security and latency on NAS hardware; default N=2^14 is a reasonable starting point.

---

### BL-031 — download_cookies_path Path Restriction

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: the `download_cookies_path` setting accepts any absolute path without validation. A malicious or mistaken value like `/etc/passwd` would be passed verbatim to yt-dlp, potentially leaking file contents.
- **Expected outcome**: validate that the path is absolute, exists, ends with `.txt`, and is readable. Optionally restrict to a configurable safe directory (env var `COOKIES_DIR`).
- **Attention point**: the check must be done at save time (POST /api/settings), not only at download time.

---

### BL-032 — MEDIA_ROOT Global Thread Safety

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: `MEDIA_ROOT` is a module-level global mutated by `POST /api/settings` without a lock. A concurrent request in `safe_path()` during the update can read a torn value, potentially allowing path traversal.
- **Expected outcome**: protect all reads and writes of `MEDIA_ROOT` with a `threading.Lock`. `safe_path()` captures the lock value once at the start of each call.
- **Attention point**: FastAPI runs handlers in threads; the lock must be non-reentrant (standard `threading.Lock` suffices).

---

### BL-033 — Job Store TTL Purge

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: the `_jobs` dict accumulates completed/errored/cancelled download jobs indefinitely. A long-running server will eventually exhaust memory.
- **Expected outcome**: after each job transitions to a terminal state (`done`, `error`, `cancelled`), schedule its removal after a configurable TTL (default 1 hour). Implement as a simple periodic cleanup triggered on job-list reads or as a background thread.
- **Attention point**: do not delete jobs that are still being polled (e.g., client checks status every second); the TTL should only apply to terminal states.

---

### BL-034 — Delete / Move: DB-First Atomicity

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: `delete_file` and `move_file` currently delete/move the file on disk first, then update the DB. If the DB write fails, the file is gone but stale progress rows remain, causing permanent inconsistency.
- **Expected outcome**: reverse the order — update the DB first, then perform the filesystem operation. If the filesystem operation fails, roll back the DB change (wrap both in a try/except with explicit rollback or re-insert).
- **Attention point**: the DB update must be committed only after the filesystem operation succeeds, or the rollback must restore the original DB state cleanly.

---

### BL-035 — SQLite Index on progress.path

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: every `/api/files` and `/api/search` call does a full table scan of `progress` to build the progress map. With large libraries this degrades linearly.
- **Expected outcome**: add `CREATE INDEX IF NOT EXISTS idx_progress_path ON progress(path)` in `init_db()`.
- **Attention point**: SQLite index creation is idempotent with `IF NOT EXISTS`; no migration tooling needed.

---

### BL-036 — Audit Logging for File Operations

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: there is no logging anywhere in `main.py`. Destructive operations (delete, move) leave no trace, making incident investigation impossible on a NAS exposed externally.
- **Expected outcome**: add `import logging` with a module-level `logger = logging.getLogger("hoard")`. Log at INFO level: file deleted, file moved, download started/completed/failed, settings changed, PIN check failed. Include client IP from `Request.client.host`.
- **Attention point**: do not log file content or PINs. Configure log level via `LOG_LEVEL` env var (default `INFO`).

---

### BL-037 — Frontend Fetch Timeout + Network Error Feedback

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: fetch calls have no timeout. If the NAS is waking from sleep or the network is slow, the UI hangs silently with no feedback. Several API calls also swallow errors with `.catch(() => null)` without showing a toast.
- **Expected outcome**: wrap fetch calls with an `AbortController` + `setTimeout` (15 s default). Replace silent `.catch(() => null)` patterns with error toasts. At minimum cover: directory listing, search, progress save, move, delete.
- **Attention point**: streaming and download-progress polling endpoints should keep their own timeout logic and not use the generic wrapper.

---

### BL-038 — Touch Gesture Discovery Overlay

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: swipe, double-tap, and triple-tap gestures are powerful but completely invisible. New users on touch devices have no way to discover them without reading the external user guide.
- **Expected outcome**: on first launch (or after a settings reset), display a one-shot modal or translucent overlay on the player area illustrating the main gesture zones (seek zones, volume swipe, double-tap). Dismissible and never shown again (flag stored in settings).
- **Attention point**: must not appear on desktop-only (non-touch) browsers; detect via `window.matchMedia('(pointer: coarse)')`.

---

### BL-039 — Accessibility: ARIA Labels, Focus Ring, Contrast

- **Dates**: `created=2026-05-09`
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: icon-only buttons have no `aria-label`; tabbing through the UI shows no focus indicator (CSS resets `outline`); `--text-dim: #666` on `--surface2: #1e1e21` is ~3:1 contrast ratio, below WCAG AA (4.5:1).
- **Expected outcome**: add `aria-label` to all interactive elements that lack visible text (home, settings, refresh, play/pause, skip, fullscreen buttons etc.); add a `:focus-visible` outline rule in CSS; raise `--text-dim` to at least `#888` or equivalent passing contrast.
- **Attention point**: aria-labels must be in French to match `lang="fr"` on the HTML element. Do not change visual design beyond contrast fix.