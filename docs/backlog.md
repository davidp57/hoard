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
| Lot 2 — BL-024 Gamepad | 70 min | ~90 min | 1.29 | 15 min | ~15 min | facteur inchangé (0,40) : dépassement lié au review Copilot (+7 fixes), pas à la complexité initiale |

> - Tickets de finition / tests simples → estimation de référence 3–5 min, pas 10–20 min.
> - Avant d'estimer un ticket de « review fix », vérifier si le problème existe réellement.
> - Pour les tickets d'implémentation technique pure, appliquer un facteur **0,60** par rapport à l'estimation initiale naïve.

---

## Lots actifs

### Lot 12 — Clavier ↔ pad : équivalence navigation arborescence (~25 min : 10 min Copilot + 15 min gestion)

> Suite directe du Lot 11. Sur PC (clavier), les touches de navigation doivent se comporter **exactement** comme le pad directionnel dans le browser : ↑/↓ = D-pad haut/bas, Entrée = A, **Échap = B (remonter d'un cran dans l'arborescence)**. Frontend-only.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-068 | Clavier — Échap = B (remonter d'un cran) + alignement complet sur le D-pad | P2 | 10 min | 2026-06-14 | 2026-06-23 | 2026-06-23 |

---

### Lot 11 — Harmonisation commandes clavier / pad / touch (~45 min : 30 min Copilot + 15 min gestion)

> Refonte complète de la cohérence des inputs. Définit un tableau de référence canonique `Commande → Clavier / Pad / Touch` et implémente tous les bindings manquants. Frontend-only, aucune modification backend. Touch non modifié dans ce lot.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-059 | Clavier — Esc enrichi (exit fullscreen + fermer player) | P1 | 5 min | 2026-05-18 | 2026-05-18 | 2026-05-19 |
| BL-060 | Clavier — ↑/↓ contextuel (navigation liste / volume) + Enter | P1 | 10 min | 2026-05-18 | 2026-05-18 | 2026-05-19 |
| BL-061 | Clavier — W (toggle watched), [ / ] (vitesse style VLC) | P2 | 5 min | 2026-05-18 | 2026-05-18 | 2026-05-19 |
| BL-062 | Pad — L3 (mute), R3 (cycle vitesse) | P2 | 5 min | 2026-05-18 | 2026-05-18 | 2026-05-19 |
| BL-063 | Help dialog — tableau de référence complet | P2 | 5 min | 2026-05-18 | 2026-05-18 | 2026-05-19 |

---

### Lot 10 — Lecteurs alternatifs : images, archives, PDF, audio (~240 min : 225 min Copilot + 15 min gestion)

> Extension de Hoard aux médias non-vidéo. Le `#player-panel` accueille 4 sous-panels (vidéo, images, PDF, audio).
> PDF.js bundlé localement dans `frontend/pdfjs/`. Archives .cbz (ZIP stdlib) + .cbr (rarfile + unrar dans Dockerfile).
> Dépendances internes : BL-054 et BL-055 dépendent de BL-053. BL-056 et BL-057 dépendent de BL-053. BL-058 dépend de tout.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-053 | Lecteurs — backend socle (media_type, /api/file, archives, CBR) | P1 | 40 min | 2026-05-15 | 2026-05-15 | 2026-05-15 |
| BL-054 | Lecteurs — visionneuse images (dossier + standalone, zoom modes) | P1 | 45 min | 2026-05-15 | 2026-05-15 | 2026-05-15 |
| BL-055 | Lecteurs — archives (.zip / .cbz / .cbr) | P1 | 30 min | 2026-05-15 | 2026-05-15 | 2026-05-15 |
| BL-056 | Lecteurs — lecteur PDF (PDF.js, keyboard/gamepad, progress) | P1 | 60 min | 2026-05-15 | 2026-05-15 | 2026-05-15 |
| BL-057 | Lecteurs — lecteur audio (native, UI dédiée) | P2 | 20 min | 2026-05-15 | 2026-05-15 | 2026-05-15 |
| BL-058 | Lecteurs — tests + intégration | P2 | 30 min | 2026-05-15 | 2026-05-15 | 2026-05-15 |

---

### Lot 5 — Fonctionnalités avancées (~125 min : 110 min Copilot + 15 min gestion)

> Dépendance interne : BL-015 dépend de BL-011 (progression multi-utilisateur présuppose une couche d'authentification) — BL-011 est dans le Lot 6 (sécurité) et doit être livré en premier.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-002 | Tri dans la liste : taille + état de lecture | P2 | 10 min | 2026-04-12 | 2026-06-23 | 2026-06-23 |
| BL-003 | Marquer manuellement vu / non vu | P2 | 10 min | 2026-04-12 | 2026-05-09 | 2026-05-09 |
| BL-006 | Renommage de fichiers/dossiers depuis l'UI | P2 | 15 min | 2026-04-12 | | |
| BL-008 | Sous-titres (`.srt` / `.ass` dans le même dossier) | P2 | 25 min | 2026-04-12 | | |
| BL-013 | Thème clair (toggle) | P3 | 20 min | 2026-04-12 | | |
| BL-066 | Plein écran fenêtré (immersif in-window) par défaut sur desktop | P2 | 15 min | 2026-06-14 | 2026-06-23 | 2026-06-23 |
| BL-015 | Progression de lecture multi-utilisateur *(dépend de BL-011)* | P2 | 35 min | 2026-04-12 | | |

---

### Lot 6 — Sécurité, Qualité & UX (~180 min : 165 min Copilot + 15 min gestion)

> Issu de la revue technique complète du 2026-05-09. Tickets ordonnés par criticité descendante.
> BL-011 est le prérequis de BL-015 (Lot 5) — livrer ce lot avant le Lot 5.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-011 | Authentification basique pour exposition hors LAN | P1 | 20 min | 2026-04-12 | 2026-06-14 | 2026-06-14 |
| BL-027 | Streaming — validation Range header (HTTP 416) | P1 | 5 min | 2026-05-09 | 2026-05-15 | 2026-05-15 |
| BL-028 | safe_path() — bloquer les symlinks dans rglob/iterdir | P1 | 10 min | 2026-05-09 | 2026-05-15 | 2026-05-15 |
| BL-029 | Security headers HTTP (X-Content-Type-Options, X-Frame-Options) | P1 | 5 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-030 | PIN — remplacer SHA-256 sans sel par scrypt | P1 | 10 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-031 | download_cookies_path — valider et restreindre le chemin | P1 | 5 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-032 | MEDIA_ROOT global — thread-safety (threading.Lock) | P2 | 10 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-033 | _jobs — purge TTL des jobs terminés (fuite mémoire) | P2 | 10 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-034 | delete/move — inverser ordre FS+DB pour atomicité | P2 | 10 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-035 | init_db() — index sur progress.path | P2 | 5 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-036 | Logging — audit trail des opérations sur fichiers | P2 | 20 min | 2026-05-09 | 2026-05-09 | 2026-06-14 |
| BL-037 | Frontend — timeout fetch + feedback réseau (AbortController) | P2 | 10 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-038 | Gestes tactiles — overlay découverte au premier lancement | P3 | 15 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-039 | Accessibilité — aria-label, :focus-visible, contraste text-dim | P3 | 20 min | 2026-05-09 | 2026-06-14 | 2026-06-14 |
| BL-064 | Fix — transcodage forcé malgré l'option désactivée | P1 | 5 min | 2026-05-18 | 2026-05-18 | 2026-05-18 |
| BL-065 | Fix — dialog d'aide clavier illisible (texte noir sur fond foncé, Firefox) | P2 | 5 min | 2026-06-14 | 2026-06-14 | 2026-06-14 |

---

### Lot 7 — Architecture & Performance (~80 min : 65 min Copilot + 15 min gestion)

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-042 | Transcoding hardware optionnel (VAAPI/NVENC) | P2 | 25 min | 2026-05-10 | | |
| BL-041 | Découpage de main.py en modules | P3 | 35 min | 2026-05-10 | | |
| BL-067 | Cleanup — supprimer l'endpoint `/api/stream` mort (legacy) | P3 | 5 min | 2026-06-14 | 2026-06-23 | 2026-06-23 |

---

## Détails

### BL-002 — Sort Controls In The File List

- **Dates**: `created=2026-04-12`, `started=2026-06-23`, `completed=2026-06-23`
- **Statut**: ✅ Réalisé — boutons **Taille** et **État** ajoutés à la barre de tri ; `sortedList()` étendu (`size` via `entry.size`, `state` via nouveau `watchStateRank()` qui mappe non-vu/en-cours/vu pour fichiers — `progress.percent` vs `cfg.watched_threshold` — et dossiers — `folder_state`). `updateSortUI()` gère l'état actif des nouveaux boutons. Options ajoutées au sélecteur de tri par défaut des réglages (`#s-sort-by`). Frontend-only (les champs `size`/`progress`/`folder_state` étaient déjà fournis par `/api/files`). Syntaxe JS validée.

- **Why**: the file list already supports sorting by name and modified date, but larger folders still need size and watch-status sorting to make the controls feel complete.
- **Expected outcome**: extend the existing sort UI so users can sort by name, modified date, size, and watch status, with a clear active state.
- **Attention point**: keep the behavior simple on both desktop and touch devices, and avoid turning the sort bar into a crowded toolbar.

### BL-003 — Manual Watched / Unwatched Toggle

- **Dates**: `created=2026-04-12`, `started=2026-05-09`, `completed=2026-05-09`
- **Statut**: ✅ Réalisé incidemment dans le commit `810f039` (BL-024 gamepad). Action `toggle_watched` disponible au pad (X) et au clavier (W) — `frontend/index.html` (~5089).
- **Reste éventuel**: le ticket évoquait aussi une action « depuis la liste » sans ouvrir la vidéo — non couvert. Rouvrir un ticket dédié si ce geste liste est souhaité.
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

- **Dates**: `created=2026-04-12`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — auth HTTP Basic **opt-in** via `HOARD_AUTH_USER` + `HOARD_AUTH_PASS` (middleware `require_basic_auth`, helper `_check_basic_auth`, comparaison `hmac.compare_digest`). Désactivée si l'une des deux vars manque → aucune régression (tests inchangés). Choix de design : Basic plutôt qu'un système de comptes, conforme à l'esprit « simple pour le self-hosting » du ticket ; multi-utilisateur (BL-015) reste séparé. Doc dev + installation EN/FR + changelog utilisateur. Tests : `TestBasicAuth`.

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

### Lot 9 — Multi-segments : sélection multi-zones et export

- **BL-047** — `created=2026-05-14`, `started=2026-05-14`, `completed=2026-05-14` — Table `segments` (id, path, seg_in, seg_out) + endpoints CRUD : `GET/POST /api/segments`, `DELETE /api/segments/{id}`. Validation `seg_out > seg_in`.
- **BL-048** — `created=2026-05-14`, `started=2026-05-14`, `completed=2026-05-14` — Export backend : mode `individual` (N fichiers, `ffmpeg -ss/-t -c copy`) et mode `merged` (concat demuxer lossless). `POST /api/files/export-segments` → job async. Déplace source + export vers destination.
- **BL-049** — `created=2026-05-14`, `started=2026-05-15`, `completed=2026-05-15` — UI seekbar : marqueurs IN/OUT colorés, fills par segment (palette cyclique), zone hachurée animée. Chips `[hh:mm → hh:mm] ×` dans `#segments-list`. Raccourcis `I` / `O` / `D`. Supprime `cutIn`/`cutOut` et les anciens boutons de découpe.
- **BL-050** — `created=2026-05-14`, `started=2026-05-15`, `completed=2026-05-15` — Modal export `#export-dialog` : toggle `individual`/`merged`, checkbox `Conserver l'original`, liste dossiers rapides, input destination, bouton Exporter. Gamepad 2 phases. Raccourci `E`/`C`.
- **BL-051** — `created=2026-05-14`, `started=2026-05-15`, `completed=2026-05-15` — Tests CRUD segments, export, range invalide. Nettoyage `TestCut`. Migration `init_db()` pour `segments`. Ruff ✓.

### Lot 8 — Gamepad : correctifs post-recette

- **BL-046** — `created=2026-05-13`, `started=2026-05-13`, `completed=2026-05-13` — `#delete-dialog` et `#move-dialog` convertis de `<dialog>` en `<div>` overlay ; déplacés dans `document.fullscreenElement` au `fullscreenchange`. `_gpDispatch` adapté pour détecter les divs ouverts.
- **BL-045** — `created=2026-05-13`, `started=2026-05-13`, `completed=2026-05-13` — Machine à états 2 phases pour `move-dialog` (phase `'folders'` → phase `'confirm'`) identique à `cut-dialog`. Bouton `#move-confirm-btn` ajouté.
- **BL-044** — `created=2026-05-13`, `started=2026-05-13`, `completed=2026-05-13` — Flag `_gpActionCooldown` (600 ms) ajouté avant tout `navigate()` post-dialog. Empêche les inputs parasites pendant le rafraîchissement async de la liste.
- **BL-043** — `created=2026-05-13`, `started=2026-05-13`, `completed=2026-05-13` — Variable `_gpPendingRestoreIdx` : sauvegardée avant `navigate()`, restaurée dans `renderFiles()` → curseur reste sur le fichier suivant après suppression/déplacement.
- **BL-052** — `created=2026-05-15`, `started=2026-05-15`, `completed=2026-05-15` — Régression BL-043 : index restauré dans `playVideo()` avant le `renderFiles(entries)` final, pour que le curseur suive la vidéo en cours en mode auto-play fullscreen.

---

### BL-027 — Streaming Range Header Validation

- **Dates**: `created=2026-05-09`, `started=2026-05-15`, `completed=2026-05-15`
- **Statut**: ✅ Réalisé dans le commit `213c452` (Lot 10 readers) sur `/api/file` — `backend/main.py` (~2303-2324) : rejet 416 pour unit non supportée, multi-range, range inversé/hors bornes. L'endpoint actif est `/api/file` ; l'ancien `/api/stream` n'est plus appelé par le frontend (code mort, parse Range naïf) → nettoyage suivi par **BL-067**.
- **Origine**: revue technique 2026-05-09 — critique.
- **Why**: the Range header parser in `/api/stream` does not validate that `start <= end` or that values are within file bounds. An inverted or out-of-bounds range can cause a 500 or unexpected behavior. Multi-range requests (`bytes=0-100,200-300`) are not handled and crash the parser.
- **Expected outcome**: return HTTP 416 (Range Not Satisfiable) for any malformed, inverted, or out-of-bounds range; ignore unsupported multi-range syntax gracefully.
- **Attention point**: must not break normal browser seeks or partial content responses.

---

### BL-028 — safe_path() Symlink Escape Fix

- **Dates**: `created=2026-05-09`, `started=2026-05-15`, `completed=2026-05-15`
- **Statut**: ✅ Réalisé dans le commit `4c0a6e2` — `backend/main.py` (~1335) : `if item.is_symlink() and not item.resolve().is_relative_to(MEDIA_ROOT.resolve())` → les symlinks qui échappent à `MEDIA_ROOT` sont exclus des listings.
- **Origine**: revue technique 2026-05-09 — critique.
- **Why**: `folder.rglob("*")` and `folder.iterdir()` follow symlinks by default. A symlink inside `MEDIA_ROOT` pointing to `/etc` passes `safe_path()` (which only checks the root) and exposes system files in directory listings.
- **Expected outcome**: for every item discovered by rglob/iterdir, skip symlinks or verify `item.resolve().is_relative_to(MEDIA_ROOT)` before including it in any response or operation.
- **Attention point**: must not break legitimate directory traversal for real nested folders.

---

### BL-029 — Security HTTP Headers Middleware

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — middleware `add_security_headers` (`@app.middleware("http")`) posant `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy` et une CSP. CSP calibrée pour ne rien casser : `'unsafe-inline'` (frontend inline), `https://fonts.googleapis.com`/`gstatic.com` (import police ligne 15 de `index.html`), `blob:`/`data:` (lecteurs média + worker PDF.js). Tests : `TestSecurityHeaders`. Doc dev EN+FR mise à jour.
- **Origine**: revue technique 2026-05-09 — critique.
- **Why**: no security headers are set. Missing `X-Content-Type-Options: nosniff` enables MIME-sniffing attacks; missing `X-Frame-Options: DENY` allows clickjacking; missing `Content-Security-Policy` reduces defense-in-depth.
- **Expected outcome**: add a `BaseHTTPMiddleware` that injects at minimum `X-Content-Type-Options`, `X-Frame-Options`, and a minimal CSP (`default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'`) on every response.
- **Attention point**: CSP must not break the single-file inline CSS/JS frontend; `unsafe-inline` is acceptable given the architecture.

---

### BL-030 — PIN Hashing: SHA-256 → scrypt

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — `_hash_pin()`/`_verify_pin()` avec `hashlib.scrypt` (stdlib), sel aléatoire 16 o, N=2^14/r=8/p=1, format `scrypt$<sel_hex>$<clé_hex>`. Comparaison constante via `hmac.compare_digest`. Migration **transparente** : `_verify_pin` accepte encore l'ancien SHA-256 sans sel, et `check_pin` réécrit le hash en scrypt à la première connexion réussie (pas de re-saisie). Tests : `TestPinHashing`.
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: PIN is currently hashed with `hashlib.sha256` with no salt. A 4-digit PIN has only 10 000 possibilities; a rainbow table cracks it instantly. A slow KDF is required for any credential storage.
- **Expected outcome**: replace with `hashlib.scrypt` (stdlib, no new dependency) with a random salt stored alongside the hash in the `settings` table. Existing stored PINs must be migrated gracefully (force re-entry on first login after upgrade).
- **Attention point**: scrypt parameters (N, r, p) must be tuned to balance security and latency on NAS hardware; default N=2^14 is a reasonable starting point.

---

### BL-031 — download_cookies_path Path Restriction

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — helper `_validate_cookies_path()` (`backend/main.py`) appelé dans `POST /api/settings` : le chemin doit être absolu, `.txt`, exister et être lisible, sinon HTTP 422. La chaîne vide réinitialise le réglage. Le garde `is_file()` côté downloader (~693) reste en défense en profondeur. Tests : 5 cas ajoutés dans `TestSettings`. La restriction optionnelle à un `COOKIES_DIR` (env var) n'a pas été implémentée (jugée superflue pour l'usage NAS mono-utilisateur ; à rouvrir si besoin).
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: the `download_cookies_path` setting accepts any absolute path without validation. A malicious or mistaken value like `/etc/passwd` would be passed verbatim to yt-dlp, potentially leaking file contents.
- **Expected outcome**: validate that the path is absolute, exists, ends with `.txt`, and is readable. Optionally restrict to a configurable safe directory (env var `COOKIES_DIR`).
- **Attention point**: the check must be done at save time (POST /api/settings), not only at download time.

---

### BL-032 — MEDIA_ROOT Global Thread Safety

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — `_media_root_lock` (`threading.Lock`) + accesseurs `get_media_root()` / `set_media_root()`. Les écritures (`reload_media_root`, `POST /api/settings`) passent par le setter ; `safe_path()` capture la racine une fois via `get_media_root()` au lieu de lire `MEDIA_ROOT` deux fois, supprimant la lecture déchirée. Tests : `TestMediaRootThreadSafety`.
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: `MEDIA_ROOT` is a module-level global mutated by `POST /api/settings` without a lock. A concurrent request in `safe_path()` during the update can read a torn value, potentially allowing path traversal.
- **Expected outcome**: protect all reads and writes of `MEDIA_ROOT` with a `threading.Lock`. `safe_path()` captures the lock value once at the start of each call.
- **Attention point**: FastAPI runs handlers in threads; the lock must be non-reentrant (standard `threading.Lock` suffices).

---

### BL-033 — Job Store TTL Purge

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — `_purge_old_jobs()` appelé au début de `GET /api/jobs` (option « déclenché à la lecture »). Les jobs en état terminal reçoivent un `_finished_at` (monotonic) à la première observation, puis sont supprimés après `JOB_TTL_SECONDS` (défaut 3600). Les jobs actifs ne sont jamais purgés. Tests : `TestJobPurge`. Doc dev (env var) EN+FR.
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: the `_jobs` dict accumulates completed/errored/cancelled download jobs indefinitely. A long-running server will eventually exhaust memory.
- **Expected outcome**: after each job transitions to a terminal state (`done`, `error`, `cancelled`), schedule its removal after a configurable TTL (default 1 hour). Implement as a simple periodic cleanup triggered on job-list reads or as a background thread.
- **Attention point**: do not delete jobs that are still being polled (e.g., client checks status every second); the TTL should only apply to terminal states.

---

### BL-034 — Delete / Move: DB-First Atomicity

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — `delete_file` et `_run_move` exécutent les `DELETE`/`UPDATE` DB (sans commit) **avant** l'opération FS, puis `commit()` si elle réussit, `rollback()` sinon. Tests : `TestDeleteMoveAtomicity` (happy path + rollback sur `PermissionError`). Note : la migration des lignes pour les fichiers *à l'intérieur* d'un dossier déplacé/supprimé reste hors périmètre (limitation préexistante).
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: `delete_file` and `move_file` currently delete/move the file on disk first, then update the DB. If the DB write fails, the file is gone but stale progress rows remain, causing permanent inconsistency.
- **Expected outcome**: reverse the order — update the DB first, then perform the filesystem operation. If the filesystem operation fails, roll back the DB change (wrap both in a try/except with explicit rollback or re-insert).
- **Attention point**: the DB update must be committed only after the filesystem operation succeeds, or the rollback must restore the original DB state cleanly.

---

### BL-035 — SQLite Index on progress.path

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé avec un écart assumé. `progress.path` est **déjà** la clé primaire (donc déjà indexée) → un `idx_progress_path` aurait été redondant et n'aurait pas aidé : le coût réel vient du balayage complet `SELECT path, position, duration FROM progress WHERE duration > 0` qui construit la carte de progression dans `/api/files`/`/api/search`. Ajout d'un **index couvrant** `idx_progress_active (duration, position, path)` permettant un balayage *index-only* (saute les lignes `duration ≤ 0`, pas de lecture de ligne). Tests : `TestSchema`.
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: every `/api/files` and `/api/search` call does a full table scan of `progress` to build the progress map. With large libraries this degrades linearly.
- **Expected outcome**: add `CREATE INDEX IF NOT EXISTS idx_progress_path ON progress(path)` in `init_db()`.
- **Attention point**: SQLite index creation is idempotent with `IF NOT EXISTS`; no migration tooling needed.

---

### BL-036 — Audit Logging for File Operations

- **Dates**: `created=2026-05-09`, `started=2026-05-09`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé. L'infra logger (`logging.getLogger("hoard")` + `LOG_LEVEL`) existait déjà (commit `67f130b`). Ajout de l'audit trail métier via le helper `_client_ip()` : `INFO` sur delete (`file deleted`), move (`file move requested`), download (`download started`/`download completed`) et `settings updated` — avec l'IP cliente ; `WARNING` sur `download failed` et `PIN check failed`. Tests : `TestAuditLogging`.
- **Origine**: revue technique 2026-05-09 — élevé.
- **Why**: there is no logging anywhere in `main.py`. Destructive operations (delete, move) leave no trace, making incident investigation impossible on a NAS exposed externally.
- **Expected outcome**: add `import logging` with a module-level `logger = logging.getLogger("hoard")`. Log at INFO level: file deleted, file moved, download started/completed/failed, settings changed, PIN check failed. Include client IP from `Request.client.host`.
- **Attention point**: do not log file content or PINs. Configure log level via `LOG_LEVEL` env var (default `INFO`).

---

### BL-037 — Frontend Fetch Timeout + Network Error Feedback

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — wrapper `apiFetch(url, opts, timeoutMs=15000)` (`AbortController` + `setTimeout`) qui affiche un toast (timeout vs erreur réseau) puis relance l'erreur. Appliqué aux appels critiques : listing (`/api/files`), recherche, sauvegarde de progression, déplacement, suppression. Streaming et polling des jobs conservent leur logique propre. Pas de test (frontend single-file sans harness) ; syntaxe JS validée via `node --check`.
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: fetch calls have no timeout. If the NAS is waking from sleep or the network is slow, the UI hangs silently with no feedback. Several API calls also swallow errors with `.catch(() => null)` without showing a toast.
- **Expected outcome**: wrap fetch calls with an `AbortController` + `setTimeout` (15 s default). Replace silent `.catch(() => null)` patterns with error toasts. At minimum cover: directory listing, search, progress save, move, delete.
- **Attention point**: streaming and download-progress polling endpoints should keep their own timeout logic and not use the generic wrapper.

---

### BL-038 — Touch Gesture Discovery Overlay

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — overlay `#gesture-help-overlay` affiché par `maybeShowGestureOverlay()` à l'ouverture du player, gardé par `window.matchMedia('(pointer: coarse)')` + `cfg.gesture_enabled` + flag. `dismissGestureOverlay()` persiste `gestures_overlay_seen` via `POST /api/settings`. Nouvelle clé settings backend (defaults/keys/payload/bools) + test `test_gestures_overlay_seen_persists`. Doc : user-guide EN/FR. Pas de test frontend (single-file) ; syntaxe JS validée via `node --check`.
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: swipe, double-tap, and triple-tap gestures are powerful but completely invisible. New users on touch devices have no way to discover them without reading the external user guide.
- **Expected outcome**: on first launch (or after a settings reset), display a one-shot modal or translucent overlay on the player area illustrating the main gesture zones (seek zones, volume swipe, double-tap). Dismissible and never shown again (flag stored in settings).
- **Attention point**: must not appear on desktop-only (non-touch) browsers; detect via `window.matchMedia('(pointer: coarse)')`.

---

### BL-039 — Accessibility: ARIA Labels, Focus Ring, Contrast

- **Dates**: `created=2026-05-09`, `started=2026-06-14`, `completed=2026-06-14`
- **Statut**: ✅ Réalisé — (1) `--text-dim` relevé #666 → #8a8a8a (≥ WCAG AA sur fond sombre) ; (2) règle globale `:focus-visible` (contour accent) ; (3) `aria-label` FR sur les contrôles icône principaux : accueil, paramètres, file de téléchargement, lecture/pause (vidéo + audio non couvert), seek ×4, plein écran, et le mute (converti en `role=button` + `tabindex` + handler clavier). Passe ciblée sur les contrôles primaires, pas un audit exhaustif de tous les boutons icône — un audit complet pourra faire l'objet d'un ticket dédié si besoin.
- **Origine**: revue technique 2026-05-09 — moyen.
- **Why**: icon-only buttons have no `aria-label`; tabbing through the UI shows no focus indicator (CSS resets `outline`); `--text-dim: #666` on `--surface2: #1e1e21` is ~3:1 contrast ratio, below WCAG AA (4.5:1).
- **Expected outcome**: add `aria-label` to all interactive elements that lack visible text (home, settings, refresh, play/pause, skip, fullscreen buttons etc.); add a `:focus-visible` outline rule in CSS; raise `--text-dim` to at least `#888` or equivalent passing contrast.
- **Attention point**: aria-labels must be in French to match `lang="fr"` on the HTML element. Do not change visual design beyond contrast fix.

---

### BL-042 — Optional Hardware Transcoding (VAAPI / NVENC)

- **Dates**: `created=2026-05-10`
- **Origine**: revue architecturale 2026-05-10 — performance NAS.
- **Why**: software H.265→H.264 transcoding is CPU-intensive and can saturate a NAS with a low-power CPU. Most modern NAS SoCs (Intel Celeron/Pentium via VAAPI, or a discrete GPU via NVENC) expose hardware video encoding that is orders of magnitude cheaper in CPU cycles.
- **Expected outcome**: add an `FFMPEG_HW_ACCEL` env var (e.g. `vaapi`, `nvenc`, empty = software fallback). When set, inject the appropriate hardware encoder flags into the ffmpeg transcode command. Document how to expose `/dev/dri` in `docker-compose.yml` for Synology. If the device is unavailable at startup, log a warning and silently fall back to software encoding.
- **Attention point**: hardware support varies by Synology model — VAAPI on Intel-based NAS, NVENC only if an external GPU is present. The option must be 100 % opt-in and never break the default software path.

---

### BL-041 — Split main.py Into Focused Modules

- **Dates**: `created=2026-05-10`
- **Origine**: revue architecturale 2026-05-10 — maintenabilité.
- **Why**: `backend/main.py` has grown to ~2 000 lines. Navigation and code review are becoming impractical. The file mixes DB setup, streaming logic, yt-dlp queue management, and FastAPI route registration — concerns that can be separated without introducing a layered architecture.
- **Expected outcome**: extract three sibling modules, keeping `main.py` as the FastAPI entry point (~600–800 lines): `backend/db.py` (init_db, get_db, inline migrations), `backend/stream.py` (streaming endpoint, ffmpeg/transcode pipeline), `backend/download.py` (yt-dlp queue, jobs dict, download endpoints). No behaviour change; all existing tests must pass without modification.
- **Attention point**: shared globals (`MEDIA_ROOT`, `FFMPEG_BIN`, `FFPROBE_BIN`) must be imported consistently across modules to avoid circular imports. Resolve by defining them in a `backend/config.py` and importing from there.

---

### BL-053 — Lecteurs : backend socle

- **Dates** : `created=2026-05-15`
- **Contexte** : pose les bases côté backend pour tous les types de médias non-vidéo.
- **Travail** :
  - Ajouter `IMAGE_EXTENSIONS`, `AUDIO_EXTENSIONS`, `PDF_EXTENSIONS = {".pdf"}`, `ARCHIVE_EXTENSIONS = {".zip", ".cbz", ".cbr"}`
  - Ajouter `is_image()`, `is_audio()`, `is_pdf()`, `is_archive()` (même pattern que `is_video()`)
  - `/api/files` : ajouter champ `media_type: "video"|"image"|"audio"|"pdf"|"archive"|"other"` (remplace les potentiels bools individuels). Retourner `progress` pour TOUS les types (pas seulement vidéo).
  - `/api/stream` → renommer en `/api/file` : retirer le guard `is_video()`, laisser `mimetypes.guess_type` déterminer le Content-Type. Conserver le support Range (utile pour images et audio). Mettre à jour le frontend en même temps.
  - Nouveaux endpoints archives :
    - `GET /api/archive/list?path=` → liste ordonnée des noms d’images dans le ZIP/CBZ/CBR (filtrée sur extensions image)
    - `GET /api/archive/image?path=&index=N` → sert l’image N depuis l’archive (réponse bytes + Content-Type)
  - `rarfile` dans `backend/requirements.txt`
  - `unrar-free` dans `Dockerfile` (apt-get install)
  - Garder `is_video()` pour la rétro-compatibilité interne mais ne plus l'exposer dans l'API

---

### BL-054 — Lecteurs : visionneuse images

- **Dates** : `created=2026-05-15`
- **Contexte** : affichage et navigation des images (fichiers isolés ou parcours d’un dossier image-only).
- **Dépend de** : BL-053
- **Travail** :
  - Nouveau panel `#image-viewer` dans `#player-panel` (masqué par défaut, visible quand `media_type === "image"`)
  - Contenu : `<img id="viewer-img">` + barre de nav (« < N / Total > ») + bouton zoom-mode
  - Deux modes d’affichage (toggle via `W` ou bouton) :
    - **page-width** : `img { width: 100%; height: auto; }` + scroll vertical libre
    - **full-page** : `img { max-width: 100%; max-height: 100vh; object-fit: contain; }` (pas de scroll)
  - Parcours d’un dossier : depuis `entries`, filtrer `media_type === "image"`, naviguer en prev/next
  - Ouvrir un fichier image isolé : charger via `/api/file?path=`
  - Progress : `position = index_courant`, `duration = total_images`, sauvegarde à chaque changement de page
  - Keyboard : `←`/`→` prev/next, `↑`/`↓` scroll (mode page-width), `W` toggle mode, `Home`/`End` 1re/dernière, `F` fullscreen, `Esc` fermer
  - Gamepad : D-←/D-→ prev/next, D-↑/D-↓ scroll, L1+D-←/→ ±10 pages, Y fullscreen, B fermer, X toggle mode
  - Icône dans liste fichiers : `📸` pour `media_type === "image"`

---

### BL-055 — Lecteurs : archives (.zip / .cbz / .cbr)

- **Dates** : `created=2026-05-15`
- **Dépend de** : BL-053, BL-054
- **Travail** :
  - Frontend : ouvrir une archive (clic/gamepad A) appelle `GET /api/archive/list?path=` pour obtenir le nombre total d'images, puis charge `/api/archive/image?path=&index=N` dans `#viewer-img`
  - Réutiliser entièrement le panel `#image-viewer` de BL-054 — seule la source des images change
  - `media_type === "archive"` dans `renderFiles` → icône `📦`
  - Distinguer le type dans le state courant (`currentMediaType`) pour que les endpoints corrects soient appelés
  - Backend : `rarfile` pour .cbr — gérer l'absence de `unrar` avec un message d'erreur clair (404 + message)

---

### BL-056 — Lecteurs : lecteur PDF (PDF.js)

- **Dates** : `created=2026-05-15`
- **Dépend de** : BL-053
- **Travail** :
  - Télécharger les fichiers `pdf.min.js` + `pdf.worker.min.js` depuis mozilla.github.io/pdf.js/releases (version 4.x) dans `frontend/pdfjs/`. FastAPI sert déjà `frontend/` comme StaticFiles → accessibles via `/pdfjs/`.
  - Nouveau panel `#pdf-viewer` : `<canvas id="pdf-canvas">` + barre nav (page N/Total) + indicateur de zoom
  - Charger le PDF via `GET /api/file?path=` (ArrayBuffer), initialiser `pdfjsLib.getDocument()`
  - Rendu page par page sur le canvas avec le zoom courant
  - Deux modes de fit (toggle `W`) : **fit-width** (zoom = container_width / page_width) et **fit-page** (zoom = min(w-ratio, h-ratio))
  - Zoom manuel : `+`/`-` (incréments 10%), clampe entre 0.5× et 4×
  - Progress : `position = page_courante`, `duration = total_pages`, sauvegarde à chaque changement
  - Keyboard : `←`/`→`/`PageUp`/`PageDown` prev/next, `↑`/`↓` scroll, `W` toggle fit, `+`/`-` zoom, `Home`/`End`, `F` fullscreen, `Esc` fermer
  - Gamepad : D-←/D-→ prev/next, D-↑/D-↓ scroll, L1+D-←/→ ±10 pages, Y fullscreen, B fermer, X toggle fit
  - Icône dans liste : `📄` pour `media_type === "pdf"`

---

### BL-057 — Lecteurs : lecteur audio

- **Dates** : `created=2026-05-15`
- **Dépend de** : BL-053
- **Travail** :
  - Réutiliser le tag `<video>` existant (les navigateurs acceptent les fichiers audio sur `<video>`) : minimal code
  - Quand `media_type === "audio"` : masquer `#video-container`, afficher un `#audio-player` dédié : artwork placeholder (icone musicale), nom du fichier, barre de progression réutilisée
  - Keyboard + gamepad identiques à la vidéo (Space, ←/→, ↑/↓ volume, D-pad), les actions qui n’ont pas de sens (fullscreen, segment IN/OUT) sont ignorées
  - Progress : time-based, identique à la vidéo (position/duration en secondes)
  - Extensions : `.mp3`, `.flac`, `.ogg`, `.m4a`, `.aac`, `.wav`, `.opus`
  - Icône dans liste : `🎵` pour `media_type === "audio"`

---

### BL-058 — Lecteurs : tests + intégration

- **Dates** : `created=2026-05-15`
- **Dépend de** : BL-053, BL-054, BL-055, BL-056, BL-057
- **Travail** :
  - Tests API (`tests/test_api.py`) :
    - `test_files_media_type` : vérifier que `/api/files` retourne le bon `media_type` pour chaque extension
    - `test_file_endpoint_image` : `/api/file?path=image.jpg` → 200 + Content-Type image/*
    - `test_file_endpoint_pdf` : `/api/file?path=doc.pdf` → 200 + Content-Type application/pdf
    - `test_archive_list_cbz` : `GET /api/archive/list?path=archive.cbz` → liste d'images
    - `test_archive_image` : `GET /api/archive/image?path=archive.cbz&index=0` → bytes + Content-Type
    - `test_archive_list_cbr` : idem pour CBR (skip si unrar absent)
    - `test_progress_non_video` : sauvegarder/lire progress pour un fichier image
  - Vérifier `ruff check` + `ruff format` à zéro warning

---

### BL-059 — Clavier : Esc enrichi (exit fullscreen + fermer player)

- **Dates** : `created=2026-05-18`
- **Lot** : Lot 11
- **Travail** :
  - Modifier le handler `Escape` dans le keyboard handler (`frontend/index.html`)
  - Après la cascade existante de fermeture des dialogs (delete, move, export, image, audio, PDF), ajouter :
    1. Si `isInFullscreen()` → `toggleFullscreen(); return;`
    2. Si `currentFile !== null` → `privacyClose(); return;`
  - Résultat : F pour entrer en fullscreen, Esc pour en sortir, Esc une 2e fois pour fermer le player — même comportement que Y puis B au pad

---

### BL-060 — Clavier : ↑/↓ contextuel (navigation liste / volume) + Enter

- **Dates** : `created=2026-05-18`
- **Lot** : Lot 11
- **Travail** :
  - Modifier les handlers `ArrowUp` / `ArrowDown` pour un comportement contextuel :
    - `currentFile !== null` (player actif) → volume ±10% (comportement actuel, inchangé)
    - `currentFile === null` (player inactif) → `_gpMoveCursor(-1)` / `_gpMoveCursor(+1)` ; si `_gpCursorIdx === -1`, initialiser au premier item visible ou à l'item actif
  - Ajouter handler `Enter` : si `_gpCursorIdx >= 0` et `currentFile === null` → `_gpActivateCursor()`
  - Réutilise le système de curseur existant du gamepad (`.gp-cursor`, `_gpMoveCursor`, `_gpActivateCursor`) — pas de nouveau code de rendu

---

### BL-061 — Clavier : W (toggle watched), [ / ] (vitesse style VLC)

- **Dates** : `created=2026-05-18`
- **Lot** : Lot 11
- **Travail** :
  - Ajouter `KeyW` dans le keyboard handler → déclenche l'action `toggle_watched` (même logique que X au pad), uniquement si `currentFile !== null`
  - Modifier `cycleSpeed()` pour accepter un paramètre `dir` (+1 par défaut) : `speedIdx = (speedIdx + dir + PLAYBACK_SPEEDS.length) % PLAYBACK_SPEEDS.length`
  - Ajouter `BracketRight` (`]`) → `cycleSpeed(+1)` et `BracketLeft` (`[`) → `cycleSpeed(-1)`, uniquement si `currentViewerMode === 'video'`

---

### BL-062 — Pad : L3 (mute), R3 (cycle vitesse)

- **Dates** : `created=2026-05-18`
- **Lot** : Lot 11
- **Travail** :
  - Ajouter `10: 'mute'` dans `GP_DEFAULT_MAPPING.base` (L3 = left stick click, actuellement non mappé)
  - Ajouter `11: 'speed_cycle'` dans `GP_DEFAULT_MAPPING.base` (R3 = right stick click, actuellement non mappé)
  - Vérifier que les cas `'mute'` et `'speed_cycle'` existent dans `_gpAction()` ; les ajouter si manquants (`cycleSpeed(+1)` pour `speed_cycle`)

---

### BL-063 — Help dialog : tableau de référence complet

- **Dates** : `created=2026-05-18`
- **Lot** : Lot 11
- **Travail** :
  - Mettre à jour le HTML statique de `<dialog id="shortcuts-dialog">` (`frontend/index.html`) pour inclure toutes les nouvelles commandes :
    - Navigation liste : ↑/↓ (player inactif) + Enter
    - Esc : exit fullscreen puis fermer player
    - W : toggle watched
    - [ / ] : vitesse −/+
    - Pad L3 : mute, R3 : cycle vitesse
  - Regrouper les raccourcis par section (Navigation, Lecture, Volume/Vitesse, Player UI, Fichiers)

---

### BL-064 — Fix : transcodage forcé malgré l'option désactivée

- **Dates** : `created=2026-05-18`
- **Lot** : Lot 6
- **Type** : bug
- **Symptôme** : Le toast « Lecture native refusée — transcodage… » s'affiche et le transcodage démarre, même quand « Transcodage activé » est désactivé dans les paramètres.
- **Cause** : Le handler `video.onerror` (frontend/index.html, ~ligne 3830) bascule inconditionnellement vers `/api/transcode` sans vérifier `cfg.transcode_enabled`. La fonction `choosePlaybackSource()` vérifie bien le flag, mais l'erreur de lecture contourne ce chemin.
- **Correction** : Ajouter un test `if (!cfg.transcode_enabled)` dans le handler `video.onerror` avant le fallback. Si désactivé, afficher un toast informatif (« Lecture non supportée nativement — activez le transcodage ») et ne pas rediriger vers `/api/transcode`.

---

### BL-065 — Fix : dialog d'aide clavier illisible (Firefox)

- **Dates** : `created=2026-06-14`
- **Lot** : Lot 6
- **Type** : bug (contraste / lisibilité)
- **Symptôme** : Sur PC (Firefox), ouvrir l'aide clavier (touche `?`) affiche un texte gris et noir sur fond gris foncé → quasiment illisible.
- **Cause** : `<dialog id="shortcuts-dialog">` (`frontend/index.html` ~ligne 1813) : le `<div>` interne a `background:var(--surface)` (#161618, foncé) mais **aucune `color` n'est définie** sur le `<dialog>` ni sur le wrapper. Les cellules de description (`<td>` sans couleur) héritent donc de la couleur par défaut du user-agent stylesheet de Firefox pour `<dialog>` (`CanvasText` ≈ noir), tandis que les en-têtes de section sont en `--text-dim` (#666, gris). Résultat : noir + gris sur fond foncé.
- **Correction** : Définir une couleur de texte explicite sur le wrapper du dialog, p. ex. `color:var(--text)` (#f0f0f0) sur le `<div>` interne. Vérifier au passage les autres `<dialog>`/overlays pour le même oubli. Optionnel (recoupe BL-039) : relever `--text-dim` au-dessus du seuil WCAG AA pour les en-têtes de section.
- **Attention** : ne pas casser le rendu des autres thèmes/overlays ; le fix doit rester purement CSS inline cohérent avec l'architecture single-file.
- **Statut** : ✅ Réalisé — `color:var(--text)` ajouté au wrapper de `#shortcuts-dialog`. Seul `<dialog>` du fichier (delete/move/export/gp-overlay sont des `<div>` héritant correctement). Le relèvement de `--text-dim` est traité dans BL-039.

---

### BL-066 — Plein écran fenêtré (immersif in-window) par défaut sur desktop

- **Dates** : `created=2026-06-14`
- **Lot** : Lot 5
- **Type** : feature (UX player)
- **Why** : sur PC, `F` / le bouton plein écran déclenchent le vrai plein écran OS (Fullscreen API). Un mode « immersif fenêtré » — vidéo qui remplit la fenêtre Firefox + UI masquée, sans sortir de la fenêtre — est souvent préférable au quotidien ; l'utilisateur garde `F11` (Firefox) pour un vrai plein écran OS.
- **Acquis** : la brique existe déjà — `toggleFullscreen()` (`frontend/index.html` ~4799) gère une classe CSS `faux-fullscreen` (position fixe plein cadre + masquage UI), aujourd'hui utilisée seulement comme *fallback* (API indisponible, ou refus Firefox+manette). `isInFullscreen()` (~4728) retourne déjà `true` pour `faux-fullscreen`.
- **Expected outcome** :
  - **Desktop (`pointer: fine`)** : `F` / bouton player / `Y` pad → activent le mode **fenêtré** (`faux-fullscreen`) par défaut. Ajouter `Shift+F` (et conserver/ajouter une affordance bouton) → **vrai** plein écran OS (`requestFullscreen`) pour qui le veut sans passer par `F11`.
  - **Tactile (`pointer: coarse`, iPad)** : comportement **inchangé** → vrai plein écran (pas de `F11` sur iPad). Détecter via `window.matchMedia('(pointer: coarse)')`.
- **Contrainte clé (demande utilisateur)** : tout le comportement « spécial plein écran » doit fonctionner à l'identique en mode fenêtré.
  - Auto-play du fichier suivant après suppression/déplacement : déjà OK, conditionné par `isInFullscreen()` (~4507, ~4579, ~4621) qui couvre `faux-fullscreen`.
  - **Point d'attention principal** : le handler `fullscreenchange` (~4830) déplace `delete-dialog` / `move-dialog` / `export-dialog` / `gp-overlay` dans `document.fullscreenElement` pour qu'ils restent visibles ; ce handler **ne se déclenche pas** en mode fenêtré. Vérifier que ces dialogs/overlays s'affichent bien par-dessus `#video-container.faux-fullscreen` (z-index / position), sinon les rattacher explicitement à l'entrée/sortie du mode fenêtré.
  - Vérifier aussi : masquage auto des contrôles, restauration du curseur gamepad, bascule du label/icône du bouton plein écran.
- **Attention** : frontend-only, aucune modif backend. Ne pas régresser le fallback existant ni le flux manette.
- **Statut** : ✅ Réalisé — `toggleFullscreen(opts)` device-aware : entrée en `faux-fullscreen` par défaut sur desktop (`pointer: fine`), vrai `requestFullscreen` si `pointer: coarse` (iPad) ou `opts.forceReal`. `Maj+F` → `toggleFullscreen({forceReal: e.shiftKey})`. Bouton/Y conservent le défaut (fenêtré sur PC). Contrainte « spécial plein écran » satisfaite : auto-play suivant via `isInFullscreen()` (couvre faux), dialogues d'action déjà gérés en faux-fullscreen (commit `d839962`). Aide clavier + user-guide EN/FR à jour. Choix : `Maj+F` plutôt qu'un bouton dédié supplémentaire (toolbar épurée). Syntaxe JS validée.

---

### BL-067 — Cleanup : supprimer l'endpoint `/api/stream` mort (legacy)

- **Dates** : `created=2026-06-14`
- **Lot** : Lot 7
- **Type** : cleanup (code mort)
- **Why** : depuis le refactoring des lecteurs (BL-053, Lot 10), le frontend ne fait plus aucun appel à `/api/stream` — tout passe par `/api/file` et `/api/transcode`. L'endpoint `/api/stream` (`backend/main.py` ~2155) subsiste donc comme code mort, et c'est le seul à garder le parse Range naïf (sans la validation 416 ajoutée par BL-027).
- **Travail** :
  - Confirmer l'absence totale de référence à `/api/stream` (frontend, docs, tests).
  - Supprimer la route `@app.get("/api/stream")` et son handler.
  - Vérifier qu'aucune doc (`docs/developer.*.md`) ne le référence encore ; mettre à jour le cas échéant.
  - `ruff check` + `pytest` au vert.
- **Attention** : si une raison de rétro-compatibilité externe existe (lien direct, marque-page), la documenter avant suppression ; sinon retirer franchement.
- **Statut** : ✅ Réalisé — route `@app.get("/api/stream")` + handler `stream_video` supprimés. Classe de tests `TestStream` retirée (couverture équivalente déjà fournie par les tests `/api/file` : range 206, multi-range, 404, traversal). Docs mises à jour (developer EN/FR, native-playback EN/FR, user-guide EN/FR) pour pointer vers `/api/file`. **Écart d'estimation** : 5 min prévus, mais les références oubliées dans tests + 6 fichiers de doc ont allongé le ticket.

---

### BL-068 — Clavier : Échap = B (remonter d'un cran) + alignement complet sur le D-pad

- **Dates** : `created=2026-06-14`
- **Lot** : Lot 12
- **Type** : feature (harmonisation inputs) — suite du Lot 11
- **Why** : sur PC (Firefox, clavier), les touches de navigation doivent reproduire **à l'identique** le pad directionnel quand on parcourt l'arborescence : flèches = D-pad, Entrée = A, Échap = B. Le besoin déclencheur : **Échap doit remonter d'un cran dans l'arborescence** (comme B), ce qui n'arrive pas aujourd'hui.
- **État actuel** (`frontend/index.html`) :
  - ↑/↓ (player inactif) → `_gpMoveCursor(∓1)` ✅ équivaut au D-pad (BL-060, ~4916-4926)
  - Entrée → `_gpActivateCursor()` ✅ équivaut à A / `nav_enter` (BL-060, ~4941)
  - **Échap** (~4855-4874) : ferme dialogs/viewers → sort du fullscreen → ferme le player ; **mais si le player est inactif, ne fait rien** → manque l'équivalent de B / `nav_back`.
  - Le pad dispose déjà de `nav_back` (~5209-5211) : `navigate(currentPath.split('/').slice(0, -1).join('/'))`.
- **Travail** :
  - Extraire une fonction `navigateUp()` à partir du corps du case `nav_back` du pad, et l'appeler des deux côtés (pad + clavier) pour garantir l'équivalence et éviter la duplication.
  - Dans le handler `Escape`, **après** la cascade existante (dialogs, viewers, fullscreen, `privacyClose`), ajouter en dernier ressort : `if (!currentFile && currentPath) { navigateUp(); return; }`.
  - Vérifier ←/→ en browser (player inactif) : aujourd'hui ils appellent `skip()` sans garde `currentFile` (~4929) → no-op au mieux. Aligner sur le D-pad gauche/droite (pas de rôle de navigation en browser) : ne rien faire si player inactif.
  - Mettre à jour `<dialog id="shortcuts-dialog">` : ligne « Échap → remonter d'un cran (player inactif) ».
- **Attention** : ne pas casser la cascade Échap existante (fermer dialog/viewer/fullscreen/player garde la priorité) ; `navigateUp()` ne doit s'appliquer qu'en dernier, browser actif et `currentPath` non racine. Frontend-only, aucune modif backend.
- **Statut** : ✅ Réalisé — `navigateUp()` factorisée et partagée par le case pad `nav_back` et le handler `Escape` (ajout `if (currentPath) { navigateUp(); return; }` en fin de cascade). Flèches ←/→ : ajout d'un garde `if (!currentFile) return;` → sans effet en mode navigation. Aide clavier mise à jour. Syntaxe JS validée (`node --check`). ↑/↓ et Entrée étaient déjà alignés (BL-060).