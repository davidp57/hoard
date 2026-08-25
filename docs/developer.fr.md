# Hoard — Guide développeur

## Vue d'ensemble

Hoard est une application web minimaliste sans framework côté frontend, avec un backend Python/FastAPI. L'ensemble est conçu pour rester simple : tout le code backend est dans `main.py`, toute l'UI est dans `index.html`.

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.12, FastAPI, uvicorn |
| Base de données | SQLite (module `sqlite3` natif, sans ORM) |
| Frontend | HTML/CSS/JS vanilla (un seul fichier) |
| Traitement vidéo | ffmpeg (via subprocess) |
| Téléchargement vidéo | yt-dlp (librairie Python, import différé) |
| Tests | pytest + httpx |
| Lint / format | ruff |
| CI/CD | GitHub Actions |
| Déploiement | Docker, docker-compose |

---

## Structure du projet

```
hoard/
├── backend/
│   ├── main.py              # Application FastAPI (toute la logique)
│   └── requirements.txt     # Dépendances production
├── frontend/
│   └── index.html           # UI complète (CSS + JS inline)
├── tests/
│   ├── conftest.py          # Fixtures pytest + isolation env
│   └── test_api.py          # Tests des endpoints API
├── .github/workflows/
│   ├── ci.yml               # Lint + tests sur chaque push / PR
│   └── docker-build.yml     # Build image Docker sur main et tags
├── docker-compose.yml       # Production (Synology)
├── docker-compose.dev.yml   # Dev override (hot-reload)
├── Dockerfile               # Image non-root + HEALTHCHECK + ffmpeg
├── pyproject.toml           # Config pytest + ruff
├── requirements-dev.txt     # Dépendances dev (tests + lint)
└── docs/                    # Documentation
```

---

## Architecture backend (`backend/main.py`)

### Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `MEDIA_ROOT` | `/media` | Racine des fichiers médias dans le container |
| `DB_PATH` | `/data/progress.db` | Chemin SQLite |
| `SSL_CERTFILE` | *(non défini)* | Chemin vers un fichier de certificat PEM. Quand défini (avec `SSL_KEYFILE`), uvicorn sert le HTTPS nativement. |
| `SSL_KEYFILE` | *(non défini)* | Chemin vers la clé privée PEM correspondante. |
| `JOB_TTL_SECONDS` | `3600` | Durée (s) de conservation en mémoire d'un job de téléchargement/export terminé avant purge. |
| `LOG_LEVEL` | `INFO` | Niveau de log du logger `hoard` (journal d'audit). |
| `LOG_DIR` | `<dossier de DB_PATH>/logs` | Dossier du fichier de log rotatif. Chaîne vide = journalisation fichier désactivée (stdout seul) — la suite de tests la met à vide. |
| `LOG_RETENTION_DAYS` | `30` | `backupCount` du `TimedRotatingFileHandler` (rotation quotidienne à minuit). |
| `RESTART_SUPERVISED` | *(auto)* | `0`/`1`. Surcharge la détection de container (`/.dockerenv`) utilisée pour formuler la confirmation de redémarrage dans l'UI. |
| `HOARD_AUTH_USER` | *(non défini)* | Identifiant pour l'auth HTTP Basic optionnelle. L'auth n'est active que si celui-ci ET `HOARD_AUTH_PASS` sont définis. |
| `HOARD_AUTH_PASS` | *(non défini)* | Mot de passe pour l'auth HTTP Basic optionnelle. |

### Sécurité des chemins

Tout accès à un fichier passe par `safe_path(rel_path)` qui vérifie que le chemin résolu reste sous `MEDIA_ROOT`. Toute tentative de path traversal retourne une 400.

```python
def safe_path(rel: str) -> Path:
    resolved = (MEDIA_ROOT / rel).resolve()
    if not str(resolved).startswith(str(MEDIA_ROOT.resolve())):
        raise HTTPException(400, "Invalid path")
    return resolved
```

### En-têtes de sécurité

Un middleware HTTP (`add_security_headers`) injecte sur chaque réponse :
`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
`Referrer-Policy: no-referrer` et une `Content-Security-Policy`. La CSP autorise
`'unsafe-inline'` (nécessaire au frontend single-file CSS/JS inline), l'import
Google Fonts (`fonts.googleapis.com` / `fonts.gstatic.com`) et les sources
`blob:`/`data:` utilisées par les lecteurs média et PDF.js. Les en-têtes sont
posés avec `setdefault`, donc un endpoint peut les surcharger si besoin.

### Auth HTTP Basic optionnelle

Définir à la fois `HOARD_AUTH_USER` et `HOARD_AUTH_PASS` impose une
authentification HTTP Basic sur chaque requête (middleware `require_basic_auth`).
Si l'une des deux n'est pas définie, l'auth est désactivée et le comportement
est inchangé. Les identifiants sont comparés en temps constant. Pensé pour
exposer Hoard derrière un reverse proxy ou en HTTPS direct sans système de
comptes — utiliser HTTPS pour ne pas transmettre les identifiants en clair.

### Endpoints API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/files?path=` | Liste le contenu d'un dossier |
| GET | `/api/progress?path=` | Lit la progression d'un fichier |
| POST | `/api/progress?path=` | Sauvegarde `{position, duration}` |
| DELETE | `/api/files?path=` | Supprime un fichier ou dossier |
| POST | `/api/files/move?path=` | Déplace vers `{destination}` (chemin relatif) |
| POST | `/api/files/mkdir` | Crée un dossier `{path}` |
| POST | `/api/files/rename?path=` | Renomme en `{new_name}` (nom seul) ; migre progress/segments, descendants de dossier inclus |
| GET | `/api/subtitles?path=` | Liste les sous-titres sidecar d'une vidéo (même dossier, même radical) |
| GET | `/api/subtitle?path=` | Sert un sous-titre converti en WebVTT (.srt/.ass → VTT, .vtt tel quel) |
| POST | `/api/files/cut` | Découpe vidéo via ffmpeg `{path, start, end, output}` |
| GET | `/api/jobs` | État des jobs background en cours (découpes ffmpeg, téléchargements) |
| GET | `/api/quick-folders` | Liste les dossiers épinglés |
| POST | `/api/quick-folders` | Épingle un dossier `{path}` |
| DELETE | `/api/quick-folders?path=` | Désépingle un dossier |
| GET | `/api/initial-sweep?path=` | Lit la config d'initial sweep effective pour un dossier |
| POST | `/api/initial-sweep` | Définit une surcharge de dossier `{path, seconds}` |
| DELETE | `/api/initial-sweep?path=` | Supprime une surcharge de dossier et revient à la valeur globale |
| GET | `/api/browse?path=` | Parcourt l'arborescence (usage : modal de déplacement) |
| GET | `/api/settings` | Lit les paramètres utilisateur |
| POST | `/api/settings` | Sauvegarde les paramètres |
| GET | `/api/media-info?path=` | Lit à la demande les métadonnées de lecture via ffprobe |
| GET | `/api/file?path=` | Sert n'importe quel fichier média (vidéo/image/audio/PDF) avec support `Range` (seeking natif) |
| GET | `/api/transcode?path=` | Stream transcodé via ffmpeg |
| GET | `/api/gallery/list?path=` | Séquence ordonnée d'une galerie (niveau courant) : `{count, items:[{path, type}]}` |
| GET | `/api/thumbnail?path=` | Vignette JPEG downscalée d'une image, à la volée (ffmpeg, sans cache) |
| GET | `/api/archive/list?path=` | Noms d'images ordonnés dans une archive ZIP/CBZ/CBR |
| GET | `/api/archive/image?path=&index=` | Sert la Nᵉ image d'une archive |
| GET | `/api/archive/thumbnail?path=&index=` | Vignette downscalée de la Nᵉ image d'archive (ffmpeg) |
| POST | `/api/download` | Télécharge une vidéo web via yt-dlp `{url, cookies?, referer?, title?}` |
| POST | `/api/jobs/{job_id}/cancel` | Annule un job de téléchargement en attente ou en cours |
| DELETE | `/api/jobs/{job_id}` | Retire un job terminé/échoué/annulé du store en mémoire |
| GET | `/api/downloads` | Historique persistant des téléchargements `?limit=&offset=&status=` → `{total, items}` |
| DELETE | `/api/downloads` | Vide tout l'historique (les fichiers ne sont pas touchés) |
| DELETE | `/api/downloads/{id}` | Retire une entrée de l'historique |
| GET | `/api/logs` | Fin du fichier de log `?lines=&level=` → `{enabled, path, retention_days, lines}` |
| POST | `/api/restart` | Termine le processus pour que le superviseur le relance `{force?}` → `{ok, supervised}` |

### Galeries

Un dossier est traité comme une **galerie** — un média unique lu page par page —
lorsqu'il est une **feuille** : plus de 3 images, aucune vidéo, et **aucun
sous-dossier** (parcours du niveau courant seulement, tri naturel). Un dossier qui
contient des sous-dossiers est un conteneur navigable : un dossier de galeries affiche
donc chaque sous-dossier comme sa propre galerie au lieu d'aplatir le tout en une seule
séquence géante. `/api/files` renvoie une galerie avec `media_type: "gallery"` et sa
propre `progress` (la reprise est ancrée sur le chemin du dossier : `position` = index
de page, `duration` = nombre de pages). Les archives (`.cbz`/`.cbr`/`.zip`) sont
l'autre support de galerie et partagent la même visionneuse.

Les fichiers non-image d'une galerie sont des **passagers** (PDF/audio/archive/texte) :
ils gardent leur position dans la séquence et reçoivent un aperçu (1ʳᵉ page PDF et texte
rendus côté client ; icône sinon). Les fichiers non pris en charge sont ignorés. La
barre de vignettes sert les **images complètes, réduites par le navigateur**
(`/api/file` / `/api/archive/image`), paresseusement (seulement au défilement) — ce qui
sort la génération de vignettes du CPU du NAS. Les endpoints ffmpeg (`/api/thumbnail`,
`/api/archive/thumbnail`) restent un repli léger, plafonnés à `THUMBNAIL_MAX_CONCURRENCY`
process simultanés (au-delà : 503), mais ne sont plus sur le chemin critique des galeries.

### Lecture native versus transcodage

Hoard récupère maintenant `/api/media-info` avant la lecture quand c'est possible, puis utilise les métadonnées de conteneur et de codecs retournées pour décider si la lecture native est vraisemblablement sûre.

Le frontend applique une échelle de décision :

1. `video.canPlayType()` sur la chaîne MIME combinant conteneur et codecs.
2. `navigator.mediaCapabilities.decodingInfo()` quand le navigateur l'expose et que les métadonnées sont assez complètes.
3. `/api/file` par défaut pour la base sûre et pour les formats `probe` comme HEVC dans MP4, même si les API de capacité du navigateur restent prudentes.
4. `/api/transcode` immédiatement seulement pour les formats `fallback` explicites, ou ensuite quand la lecture native échoue malgré tout au chargement réel.

Voir `docs/native-playback.fr.md` pour la matrice de compatibilité et la stratégie désormais implémentée.

### Schéma SQLite

```sql
CREATE TABLE progress (
    path TEXT PRIMARY KEY,
    position REAL DEFAULT 0,
    duration REAL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quick_folders (
    path TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE initial_sweep_folders (
    path TEXT PRIMARY KEY,
    seconds INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE downloads (
    id          TEXT PRIMARY KEY,   -- uuid du job
    url         TEXT NOT NULL,
    title       TEXT,               -- indice de titre envoyé par la bookmarklet
    output_name TEXT,               -- nom de fichier final
    output_path TEXT,               -- chemin relatif à MEDIA_ROOT
    status      TEXT NOT NULL,      -- pending|resolving|running|done|error|cancelled|interrupted
    error       TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP
);
-- index : idx_downloads_created ON downloads(created_at DESC)
```

### Initial Sweep

L'initial sweep permet à Hoard de démarrer une **vidéo neuve** à un offset configuré au lieu de `0`.

- Valeur globale par défaut : stockée dans la table `settings` sous la clé `initial_sweep_seconds`
- Surcharge par dossier : stockée dans `initial_sweep_folders`, indexée par chemin relatif de dossier
- Action player : la position de lecture actuelle peut être enregistrée directement comme surcharge de dossier via un contrôle compact unique dans le player
- La surcharge de dossier gagne sur la valeur globale
- `0` signifie désactivé
- Une progression de lecture déjà sauvegardée gagne toujours sur toute règle d'initial sweep

### Jobs en arrière-plan

Les découpes vidéo (`/api/files/cut`) s'exécutent dans des threads daemon individuels. Les téléchargements web utilisent une file séquentielle :

- **Phase 1 (thread immédiat)** : à l'appel de `POST /api/download`, un thread dédié démarre immédiatement, passe le job en `resolving`, remplit un aperçu du nom de fichier depuis l'indice `title`, puis passe en `pending` et ajoute le job à la `queue.Queue`.
- **Phase 2 (worker de file)** : un seul thread daemon (`dl-worker`) défile les jobs un par un et exécute le téléchargement yt-dlp, évitant la surcharge de bande passante.

**Cycle de vie du statut d'un job :** `pending` → `resolving` → `pending` (avec nom de fichier) → `running` → `done` / `error` / `cancelled`. Les lignes d'historique peuvent en plus porter `interrupted`, positionné au démarrage pour les jobs que le processus n'a jamais terminés.

Tout l'état des jobs est conservé en mémoire dans `_jobs : dict[str, dict]`. Les champs préfixés par `_` sont privés et retirés avant la sérialisation JSON par `_job_for_api()`. L'endpoint `/api/jobs` permet au frontend de poller l'état.

**Persistance des téléchargements.** `_jobs` n'est que le store chaud : les entrées sont purgées `JOB_TTL_SECONDS` après leur état terminal et disparaissent au redémarrage. Chaque transition significative d'un job `download` est donc recopiée dans la table `downloads` par `_persist_download()`, que l'historique `/api/downloads` relit. Une erreur DB y est journalisée et absorbée : la persistance ne doit jamais casser un téléchargement.

Au démarrage, `mark_interrupted_downloads()` bascule en `interrupted` toute ligne encore dans un état non terminal — le processus est mort en plein téléchargement, et sans ça l'historique afficherait des jobs éternellement `running`. La rétention est pilotée par le réglage `download_history_days` (`0` = illimité, le défaut) et appliquée par `_purge_download_history()`.

**Résilience du worker (BL-078).** `_download_worker_loop` intercepte désormais toute exception échappant à `_run_download`. Avant ce correctif, une erreur inattendue (import yt-dlp cassé, job retiré en cours de route) remontait hors de la boucle `while True` et **tuait définitivement** le thread `dl-worker` : tous les téléchargements suivants restaient alors en `pending` pour toujours, sans erreur visible nulle part. Le handler journalise la trace, passe le job en `error` et garde le thread vivant.

**Skip silencieux (BL-079).** yt-dlp **n'écrase pas** un fichier existant et **ne lève rien** quand il saute le téléchargement : `extract_info(download=True)` revient normalement et le hook de progression émet quand même `finished`. Hoard lisait ça comme un succès : un téléchargement dont le nom était déjà pris passait `done` sans qu'aucun fichier soit écrit. La bookmarklet envoyant `document.title`, et un même site donnant souvent le même titre à toutes ses vidéos, la perte était massive. Trois garde-fous :

1. `_unique_output_stem()` libère le nom en amont (`Video.mp4` → `Video (2).mp4`), en testant le préfixe `stem + "."` via `iterdir()` — pas `glob()`, un stem pouvant contenir `[`.
2. Le hook de progression compte les événements `downloading`. Zéro événement = aucun octet transféré, donc un skip ; le job passe en `error` en expliquant la collision. C'est le filet pour les téléchargements lancés sans titre, dont le nom ne peut pas être réservé à l'avance.
3. `_confirm_download_landed()` refuse de marquer un job `done` sans constater le fichier sur le disque, et journalise le chemin absolu et la taille.

Le nom stocké vient de `info["requested_downloads"][0]["filepath"]` — ce que yt-dlp a réellement écrit. L'ancien code le reconstruisait via `prepare_filename()` en forçant le suffixe `merge_output_format` : un flux unique écrit en `.webm` était enregistré comme un `.mp4` inexistant.

Les titres passent par `_outtmpl_literal()` avant d'entrer dans le template de sortie : `%` introduit un champ, si bien que `Best of 50%(off) deal` produisait le fichier `Best of 50NAeal.mp4`.

### Endpoint de téléchargement (`POST /api/download`)

**Corps de la requête** (`DownloadRequest`) :

```json
{ "url": "https://cdn.example.com/video.mp4", "cookies": "name=value; other=foo", "referer": "https://example.com/posts/123" }
```

- `url` — requis. URL de la page web ou de la vidéo directe.
- `cookies` — optionnel. Chaîne `document.cookie` brute capturée par la bookmarklet. Convertie au format Netscape et transmise à yt-dlp.
- `referer` — optionnel. URL de la page d'origine. Quand fourni, envoyé comme en-tête HTTP `Referer` pour que les CDN qui vérifient l'origine acceptent la requête. La bookmarklet le renseigne automatiquement quand une source `<video>` directe est détectée.

**Réponse :**

```json
{ "job_id": "abc123" }
```

**Sécurité (protection SSRF) :** L'endpoint rejette les URL `file://` et tout hôte résolvant vers localhost ou les plages RFC-1918 (`127.*`, `::1`, `192.168.*`, `10.*`, `172.*`).

**Ordre de résolution des cookies :**
1. Fichier `cookies.txt` persistant (chemin depuis le paramètre `download_cookies_path`), s'il existe.
2. Cookies inline du corps de requête, écrits dans un fichier temporaire.

Le paramètre `download_cookies_path` est validé à l'enregistrement via `POST /api/settings` (`_validate_cookies_path()`) : le chemin doit être absolu, se terminer par `.txt`, exister et être lisible, sinon l'enregistrement est rejeté avec un code HTTP 422. Une chaîne vide réinitialise le paramètre. Cela empêche de pointer yt-dlp vers un fichier arbitraire.

**Options yt-dlp utilisées :** `bestvideo+bestaudio/best`, `merge_output_format: mp4`. La sortie est sauvegardée dans le paramètre `download_folder` (relatif à `MEDIA_ROOT`, créé si nécessaire).

---

## Architecture frontend (`frontend/index.html`)

Le frontend est un fichier HTML unique avec CSS et JS inline. Aucun framework, aucun bundler.

### Organisation du JS

Le code JS est organisé en sections fonctionnelles commentées :

- **Config & state** : constantes, variables globales
- **API helpers** : fonctions `fetch` réutilisables
- **Navigation** : chargement de dossier, breadcrumb, cache LRU
- **File list rendering** : rendu de la liste de fichiers
- **Player** : contrôles, seekbar, sauvegarde de position
- **Touch gestures** : gestion des événements tactiles
- **Keyboard shortcuts** : gestionnaire `keydown`
- **Modals** : move, browse, cut
- **Quick folders** : épingles

### Variables CSS

Tous les tokens de couleur sont définis dans `:root` :

```css
:root {
  --bg: #0e0e0f;
  --surface: #161618;
  --accent: #e8ff47;
  --seen: #3a5a3a;
  --inprogress: #5a4a1a;
  /* ... */
}
```

### Responsive

- Breakpoint à **700 px** : au-delà, vue divisée (liste + player). En dessous, liste plein écran et player en overlay.
- `dvh` utilisé partout pour éviter les problèmes d'unité viewport sur mobile.

### Shell PWA

- `frontend/manifest.webmanifest` fournit les métadonnées d'installation pour les navigateurs compatibles et les lanceurs home-screen.
- `frontend/service-worker.js` ne met en cache que le shell applicatif (`/`, favicon, manifest) et évite explicitement les requêtes `/api/*`, donc l'installabilité ne signifie pas navigation ou lecture NAS hors ligne.
- Le frontend enregistre le service worker uniquement en contexte sécurisé et applique les marges safe-area pour que le shell standalone se comporte mieux sur tablette et en lancement home-screen iOS.

---

## Développement local

### Setup rapide

```bash
git clone https://github.com/davidp57/hoard.git
cd hoard
python -m venv .venv
.venv\Scripts\activate          # ou: source .venv/bin/activate
pip install -r requirements-dev.txt

$env:MEDIA_ROOT = "$(pwd)\dev-media"
$env:DB_PATH    = "$env:TEMP\hoard-dev.db"
uvicorn backend.main:app --reload --port 8000
```

### Script de développement

```powershell
# dev.ps1 — lance le serveur avec les variables appropriées
.\dev.ps1
```

---

## Tests

```bash
python -m pytest tests/ -v
```

Les tests utilisent `httpx.AsyncClient` avec `TestClient` de FastAPI. Chaque test s'exécute dans un répertoire temporaire isolé (`tmp_path`). La configuration ruff et pytest est dans `pyproject.toml`.

Rapport de couverture généré dans `coverage.xml`.

---

## Lint et format

```bash
ruff check .          # lint
ruff format --check . # vérification de format
ruff format .         # formatage
```

---

## CI/CD

### ci.yml

Déclenché sur chaque push et PR :
1. `ruff check .`
2. `ruff format --check .`
3. `python -m pytest tests/ -v --cov`

### docker-build.yml

Déclenché sur push sur `main` et sur les tags `v*.*.*` :
- Build multi-platform (`linux/amd64`, `linux/arm64`)
- Push sur `ghcr.io/davidp57/hoard`
- Tag `main` pour `main`, tag semver pour les releases

---

## Conventions

- **Pas d'ORM** : toutes les requêtes SQLite sont écrites à la main avec des paramètres liés (`?`).
- **Pas de breaking change API** sans mettre à jour ce fichier et `docs/installation.*.md`.
- **Typage Pydantic** uniquement pour les request bodies POST.
- Les **chemins** sont toujours stockés et transmis **relatifs à `MEDIA_ROOT`**.
- Variables CSS pour tous les tokens de couleur, aucune couleur hardcodée dans le HTML.
- Un seul `index.html` : ne pas fragmenter le frontend en plusieurs fichiers.

---

## Ajouter un endpoint

1. Ajouter la fonction dans `backend/main.py` avec son decorator `@app.<method>`.
2. Ajouter le cas de test dans `tests/test_api.py`.
3. Mettre à jour le tableau des endpoints dans ce fichier et dans `CLAUDE.md`.
4. Implémenter l'appel côté frontend dans `frontend/index.html`.
