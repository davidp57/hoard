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

### Lot 8 — Gamepad : correctifs post-recette (~80 min : 65 min Copilot + 15 min gestion)

> Bugs identifiés lors des tests sur SteamDeck (Edge, Docker `develop`, port 8100).
> BL-046 est un prérequis naturel de BL-045 (si on convertit move-dialog en div dans BL-046, la 2-phase de BL-045 s'appuie sur la nouvelle structure).

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-046 | Gamepad — delete-dialog et move-dialog cassés en fullscreen | P1 | 25 min | 2026-05-13 | 2026-05-13 | 2026-05-13 |
| BL-045 | Gamepad — move dialog : ajouter phase de confirmation (A/B) | P1 | 15 min | 2026-05-13 | 2026-05-13 | 2026-05-13 |
| BL-044 | Gamepad — vidéo démarre en fond sonore après action dialog | P1 | 15 min | 2026-05-13 | 2026-05-13 | 2026-05-13 |
| BL-043 | Gamepad — curseur remis à zéro après suppression/déplacement/split | P2 | 10 min | 2026-05-13 | 2026-05-13 | 2026-05-13 |
| BL-052 | Gamepad — curseur à -1 après auto-play post-suppression (régression BL-043) | P1 | 10 min | 2026-05-15 | 2026-05-15 | 2026-05-15 |

---

### Lot 10 — Lecteurs alternatifs : images, archives, PDF, audio (~240 min : 225 min Copilot + 15 min gestion)

> Extension de Hoard aux médias non-vidéo. Le `#player-panel` accueille 4 sous-panels (vidéo, images, PDF, audio).
> PDF.js bundlé localement dans `frontend/pdfjs/`. Archives .cbz (ZIP stdlib) + .cbr (rarfile + unrar dans Dockerfile).
> Dépendances internes : BL-054 et BL-055 dépendent de BL-053. BL-056 et BL-057 dépendent de BL-053. BL-058 dépend de tout.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-053 | Lecteurs — backend socle (media_type, /api/file, archives, CBR) | P1 | 40 min | 2026-05-15 | | |
| BL-054 | Lecteurs — visionneuse images (dossier + standalone, zoom modes) | P1 | 45 min | 2026-05-15 | | |
| BL-055 | Lecteurs — archives (.zip / .cbz / .cbr) | P1 | 30 min | 2026-05-15 | | |
| BL-056 | Lecteurs — lecteur PDF (PDF.js, keyboard/gamepad, progress) | P1 | 60 min | 2026-05-15 | | |
| BL-057 | Lecteurs — lecteur audio (native, UI dédiée) | P2 | 20 min | 2026-05-15 | | |
| BL-058 | Lecteurs — tests + intégration | P2 | 30 min | 2026-05-15 | | |

---

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

### Lot 7 — Architecture & Performance (~75 min : 60 min Copilot + 15 min gestion)

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-042 | Transcoding hardware optionnel (VAAPI/NVENC) | P2 | 25 min | 2026-05-10 | | |
| BL-041 | Découpage de main.py en modules | P3 | 35 min | 2026-05-10 | | |

---

### Lot 9 — Multi-segments : sélection multi-zones et export (~130 min : 115 min Copilot + 15 min gestion)

> Remplace le système IN/OUT → découper par une sélection multi-segments persistée en base.
> L'utilisateur place autant de paires IN/OUT qu'il veut, puis exporte en N fichiers séparés ou en un seul fichier fusionné (concat lossless FFmpeg).
> Dépendances internes : BL-049, BL-050 et BL-051 dépendent de BL-047 et BL-048.

| ID | Titre | Prio | Est. | Créé | Démarré | Terminé |
| --- | --- | --- | --- | --- | --- | --- |
| BL-047 | Segments — table DB + endpoints CRUD | P1 | 20 min | 2026-05-14 | 2026-05-14 | 2026-05-14 |
| BL-048 | Segments — export backend (individuel + fusionné) | P1 | 25 min | 2026-05-14 | 2026-05-14 | 2026-05-14 |
| BL-049 | Segments — UI seekbar + liste chips (frontend) | P1 | 35 min | 2026-05-14 | 2026-05-27 | 2026-05-27 |
| BL-050 | Segments — modal export + gamepad (frontend) | P1 | 20 min | 2026-05-14 | 2026-05-27 | 2026-05-27 |
| BL-051 | Segments — tests + nettoyage ancien cut | P2 | 15 min | 2026-05-14 | 2026-05-27 | 2026-05-27 |

---

## Détails

### BL-046 — Gamepad : delete-dialog et move-dialog cassés en fullscreen

- **Dates** : `created=2026-05-13`
- **Contexte** : testé sur SteamDeck / Edge, Docker `develop` port 8100.
- **Symptôme** : en mode plein écran natif, les dialogues de suppression et de déplacement s'affichent mais les boutons gamepad n'ont aucun effet (ni A pour confirmer, ni B pour annuler).
- **Cause racine** : `#delete-dialog` et `#move-dialog` utilisent `<dialog>` + `showModal()`. Sur SteamDeck/Edge en fullscreen natif, les éléments `<dialog>` sont rendus dans le « top layer » du navigateur, mais n'y reçoivent pas les événements correctement — exactement le même bug que `#gp-overlay` (corrigé en convertissant la dialog en `<div>` et en la déplaçant dans `document.fullscreenElement` au `fullscreenchange`). De plus, `document.querySelector('dialog[open]')` peut retourner `null` si l'attribut `open` n'est pas positionné de la même façon sur un `<div>`.
- **Correction proposée** : convertir `#delete-dialog` et `#move-dialog` de `<dialog>` en `<div>` overlay (même pattern que les autres modals `<div>` de l'app : `display:none` / `display:flex`, `position:fixed`, `z-index`). Adapter `confirmDelete()`, `openMoveModal()`, `closeModal()`. Déplacer les deux divs dans `document.fullscreenElement` lors du `fullscreenchange` (comme `#gp-overlay`). Adapter `_gpDispatch` pour détecter les divs ouverts au lieu de `dialog[open]`.
- **Attention** : `<dialog>` offre le comportement `Escape` natif et le backdrop — il faudra les recréer explicitement pour la fermeture clavier et le clic backdrop.

---

### BL-045 — Gamepad : move dialog — ajouter phase de confirmation (A/B)

- **Dates** : `created=2026-05-13`
- **Contexte** : dépend de BL-046 (si move-dialog est converti en div dans BL-046, adapter en conséquence).
- **Symptôme** : dans le move dialog, appuyer sur A avec le gamepad déclenche immédiatement le déplacement du fichier, sans étape de confirmation. Il n'y a pas de bouton « OK » ni « Annuler » dans le flux gamepad.
- **Cause racine** : `_gpHandleDialog` pour `move-dialog` appelle directement `btns[_gpMoveDlgIdx]?.click()` → `moveToFolder()` sans 2ème phase. Contrairement au `cut-dialog` qui a un `_gpPhase` ('folders' → 'confirm').
- **Correction proposée** : ajouter une machine à états à 2 phases dans `_gpHandleDialog` pour `move-dialog` (identique à `cut-dialog`) : phase `'folders'` — D↑/↓ navigue les dossiers, A → sélectionne le dossier et passe en phase `'confirm'` en focalisant le bouton Confirmer ; phase `'confirm'` — A exécute le déplacement, B revient en phase `'folders'`. B annule le dialog depuis n'importe quelle phase. Ajouter un bouton « Confirmer » (`id="move-confirm-btn"`) visible dans le HTML du modal, et lui appliquer la classe `.gp-cursor` quand il est focalisé.

---

### BL-044 — Gamepad : vidéo démarre en fond sonore après action dialog

- **Dates** : `created=2026-05-13`
- **Symptôme** : parfois, après avoir confirmé/annulé un dialogue (suppression, déplacement) via le gamepad, une vidéo se met à jouer en arrière-plan — l'audio est audible alors que l'UI affiche la liste et qu'aucune vidéo n'est ouverte par l'utilisateur.
- **Cause racine** : race condition async. Quand A confirme la suppression, `dlg.close()` s'exécute de façon synchrone, mais `await navigate(currentPath)` est asynchrone. Pendant la fenêtre async (avant que `renderFiles()` remette `_gpCursorIdx = -1`), `_gpCursorIdx` pointe encore un fichier valide et `currentFile = null`. Si A est re-pressé dans cette fenêtre (micro-rebond de bouton, ou l'utilisateur appuie rapidement), `_gpDispatch` ne voit plus de dialog ouvert → chemin browser nav → `nav_enter` → `_gpActivateCursor()` → `playVideo()`. La vidéo démarre mais le player ne s'affiche pas si la navigation a déjà effacé `currentFile`.
- **Correction proposée** : ajouter un flag `_gpActionCooldown` (timestamp) positionné juste avant tout appel à `navigate()` après une action dialog. Dans `_gpDispatch`, si `Date.now() < _gpActionCooldown`, ignorer tous les inputs sauf les modificateurs. Durée de cooldown : 600 ms (suffisant pour couvrir un `navigate()` normal). Alternative plus simple : réinitialiser `_gpCursorIdx = -1` immédiatement lors du lancement d'une action qui va rafraîchir la liste (avant l'`await`).

---

### BL-043 — Gamepad : curseur remis à zéro après suppression/déplacement/split

- **Dates** : `created=2026-05-13`
- **Symptôme** : après avoir supprimé, déplacé ou découpé un fichier via le gamepad, le curseur de navigation revient au début de la liste (`_gpCursorIdx = -1`). L'utilisateur doit re-parcourir toute la liste depuis le début pour atteindre le fichier suivant.
- **Comportement attendu** : après l'action, le curseur reste à l'index N (qui pointe maintenant sur le fichier qui était à N+1 avant la suppression, ou reste sur N si N < nouvelle longueur, ou sur le dernier élément sinon).
- **Cause racine** : `renderFiles()` (ligne ~3039) appelle toujours `_gpCursorIdx = -1`. Toutes les actions fichier appellent `navigate(currentPath)` → `renderFiles()`. Il n'existe aucun mécanisme pour persister ou restaurer le curseur entre deux rendus.
- **Correction proposée** : avant l'appel à `navigate()` dans les actions delete, move et split (cut), sauvegarder `_gpCursorIdx` dans une variable module `_gpPendingRestoreIdx`. Dans `renderFiles()`, après avoir calculé `_gpRenderedList`, si `_gpPendingRestoreIdx >= 0`, restaurer `_gpCursorIdx = Math.min(_gpPendingRestoreIdx, _gpRenderedList.length - 1)` et appeler `_gpMoveCursor(0)` pour mettre à jour le highlight DOM, puis réinitialiser `_gpPendingRestoreIdx = -1`.

---

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

### BL-047 — Segments : table DB + endpoints CRUD

- **Dates** : `created=2026-05-14`
- **Contexte** : socle du Lot 9. Remplace les colonnes `cut_in`/`cut_out` de `progress` par une table dédiée.
- **Schéma** :
  ```sql
  CREATE TABLE IF NOT EXISTS segments (
      id       INTEGER PRIMARY KEY AUTOINCREMENT,
      path     TEXT NOT NULL,
      seg_in   REAL NOT NULL,
      seg_out  REAL NOT NULL
  );
  CREATE INDEX IF NOT EXISTS idx_segments_path ON segments(path);
  ```
  Les colonnes `cut_in`/`cut_out` restent dans `progress` (rétrocompatibilité) mais ne sont plus écrites par le nouveau flow.
- **Endpoints** :
  - `GET  /api/segments?path=<file>` → liste `[{id, seg_in, seg_out}]` ordonnés par `id ASC`
  - `POST /api/segments?path=<file>` body `{seg_in, seg_out}` → `{id}` (valide `seg_out > seg_in`)
  - `DELETE /api/segments/{id}` → supprime le segment par `id` (404 si inconnu)
- **Modèle Pydantic** : `SegmentCreate(seg_in: float, seg_out: float)`
- **Attention** : `safe_path()` sur le paramètre `path`. Valider `seg_out > seg_in` (400 sinon).

---

### BL-048 — Segments : export backend (individuel + fusionné)

- **Dates** : `created=2026-05-14`
- **Contexte** : dépend de BL-047. Fournit l'endpoint d'export et deux stratégies FFmpeg.
- **Endpoint** : `POST /api/files/export-segments?path=<file>`
  - Body : `{mode: "individual"|"merged", destination: str, keep_original: bool = false}`
  - Récupère la liste des segments depuis la table `segments` pour ce `path` (erreur 400 si aucun segment)
  - Lance un job async → retourne `{job_id}`
- **Mode `individual`** : N jobs FFmpeg successifs (dans le même thread), un par segment :
  ```
  ffmpeg -ss <in> -t <dur> -i input -c copy "nom [seg1].ext"
  ```
  Nommage : `{stem} [seg{N}]{ext}` (N basé sur la position dans la liste).
- **Mode `merged`** *(défaut)* : un seul FFmpeg avec le concat demuxer (lossless, codec copy) :
  ```
  # filelist.txt
  file 'input.mp4'
  inpoint 10.5
  outpoint 30.2
  file 'input.mp4'
  inpoint 45.0
  outpoint 90.0
  ```
  ```
  ffmpeg -f concat -safe 0 -i filelist.txt -c copy "nom [1-N segments].ext"
  ```
  Nommage : `{stem} [{N} segments]{ext}`.
- **Post-export** : déplace **les deux fichiers** vers `destination` — le fichier exporté (ou les N fichiers en mode individual) ET le fichier source original. C'est le comportement par défaut (`keep_original=false`). Si `keep_original=true`, seul(s) le(s) fichier(s) exporté(s) sont déplacés, l'original reste en place.
- **Tracking progression** : même pattern que `_run_cut` (stderr `time=` regex, job `status`/`progress`).
- **Attention** : le concat demuxer requiert que tous les segments soient du même codec. Ajouter un warning dans le toast si le mode merged est demandé sur un fichier transcodé.
- **Garder** : l'endpoint `/api/files/cut` en place (pas supprimé) mais marqué comme déprécié dans le code.

---

### BL-049 — Segments : UI seekbar + liste chips (frontend)

- **Dates** : `created=2026-05-14`
- **Contexte** : dépend de BL-047. Remplace entièrement le flow `cutIn`/`cutOut` dans le frontend.
- **État global** :
  ```js
  let _pendingIn = null;         // IN posé, attend un OUT
  let _segments  = [];           // [{id, seg_in, seg_out}, …] chargés depuis DB ou ajoutés localement
  ```
- **Flux** :
  1. `I` → `setPendingIn()` : pose `_pendingIn = video.currentTime`, affiche marqueur bleu sur seekbar, toast « IN marqué »
  2. `O` → `addSegment()` : POST `/api/segments`, ajoute `{id, seg_in:_pendingIn, seg_out:currentTime}` à `_segments`, remet `_pendingIn = null`, met à jour la seekbar et la liste chips, toast « Segment N ajouté »
  3. `×` sur une chip → `deleteSegment(id)` : DELETE `/api/segments/{id}`, retire de `_segments`, met à jour l'UI
  4. Cliquer sur une chip → seek à `seg_in`
- **Seekbar** : fills colorés par segment (palette cyclique : accent / orange / vert / violet…). Pendant qu'un IN est posé sans OUT, zone hachurée animée entre `_pendingIn` et la tête de lecture courante.
- **Liste chips** : `<div id="segments-list">` juste sous `#seekbar-wrap`, visible uniquement si `_segments.length > 0`. Chips : `[0:10 → 1:30] ×` — format compact `formatTime()`.
- **Bouton exporter** : `<button id="segments-export-btn">` dans la barre de contrôle (remplace `#cut-btn`). Label : « Exporter (N) ✂ ». `display:none` si `_segments.length == 0`.
- **Chargement** : `loadSegments(path)` appelé dans `playVideo()` → GET `/api/segments?path=…` → peuple `_segments` et rafraîchit l'UI.
- **Raccourcis** : `I` = IN, `O` = OUT/créer segment, `Backspace` (déjà en place pour delete) non utilisé ici → garder `D` pour deleteLastSegment.
- **Retirer** : variables `cutIn`, `cutOut`, fonctions `setCutPoint`, `clearCutPoints`, `updateCutUI`, boutons `#cut-in-btn`, `#cut-out-btn`, `#cut-clear-btn`, `#cut-btn`, HTML `#cut-seekbar-fill`, `.cut-seekbar-marker`, dialog `#cut-dialog`.

---

### BL-050 — Segments : modal export + gamepad (frontend)

- **Dates** : `created=2026-05-14`
- **Contexte** : dépend de BL-048 et BL-049. Modal d'export remplaçant `#cut-dialog`.
- **HTML** : `<div id="export-dialog">` overlay (même pattern que les autres modals div).
  - Toggle `individual` / `merged` *(merged sélectionné par défaut)*
  - Checkbox `Conserver l'original` (défaut : décoché — déplace l'original ET les fichiers exportés vers destination)
  - Liste de dossiers rapides (même que cut-dialog)
  - Input destination libre
  - Bouton `Exporter`
- **Fonctions** : `openExportModal()`, `closeExportModal()`, `confirmExport()` → POST `/api/files/export-segments`.
- **Gamepad** : navigation dans les dossiers rapides + sélection mode + confirmation (même pattern 2-phases que move-dialog/cut-dialog).
- **Toast** : « ✂ Export N segments en cours… » / « ✂ Export fusionné en cours… »
- **Raccourci** : `E` ou `C` pour ouvrir le modal (remplace l'ancien `C`).

---

### BL-051 — Segments : tests + nettoyage ancien cut

- **Dates** : `created=2026-05-14`
- **Contexte** : finalise le Lot 9. À faire en dernier.
- **Tests à ajouter** (`tests/test_api.py`) :
  - `test_segments_crud` : POST → GET → DELETE, vérifier la liste avant/après
  - `test_segment_invalid_range` : `seg_out <= seg_in` → 400
  - `test_export_segments_no_segments` : appel sans segments → 400
  - `test_export_individual_returns_job_id` (monkeypatch ffmpeg)
  - `test_export_merged_returns_job_id` (monkeypatch ffmpeg)
  - `test_export_dest_not_found` → 404
- **Nettoyage** :
  - Supprimer les tests `TestCut` obsolètes ou les adapter si `/api/files/cut` est gardé déprécié
  - Ajouter `ADD COLUMN` migration dans `init_db()` pour la table `segments` si elle n'existe pas (rétrocompat bases existantes)
  - Vérifier que `ruff check` + `ruff format` passent à zéro warning

---

### BL-052 — Gamepad : curseur à -1 après auto-play post-suppression (régression BL-043)

- **Dates** : `created=2026-05-15`
- **Contexte** : régression introduite lors de l'implémentation de `_autoPlayNextFullscreen` (PR #19). Après une suppression en plein écran, le fichier suivant est lancé via `playVideo()`. À la fin de `playVideo`, `renderFiles(entries)` est appelé alors que `_gpPendingRestoreIdx = -1` (déjà consommé par le `renderFiles` de `navigate`), ce qui déclenche la branche `else { _gpCursorIdx = -1; }` dans `renderFiles`. Résultat : curseur gamepad à -1, commandes buggées, risque de vidéo fantôme (régression BL-044).
- **Fichiers modifiés** :
  - `frontend/index.html` — fin de `playVideo()` : ajout de `_gpPendingRestoreIdx = gpIdx` avant `renderFiles(entries)`
- **Fix** : avant le `renderFiles(entries)` final de `playVideo`, rechercher `entry.path` dans `_gpRenderedList` et stocker l'index dans `_gpPendingRestoreIdx`. Ainsi, `renderFiles` restaure le curseur sur la vidéo en cours de lecture.

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