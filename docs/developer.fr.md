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

### Sécurité des chemins

Tout accès à un fichier passe par `safe_path(rel_path)` qui vérifie que le chemin résolu reste sous `MEDIA_ROOT`. Toute tentative de path traversal retourne une 400.

```python
def safe_path(rel: str) -> Path:
    resolved = (MEDIA_ROOT / rel).resolve()
    if not str(resolved).startswith(str(MEDIA_ROOT.resolve())):
        raise HTTPException(400, "Invalid path")
    return resolved
```

### Endpoints API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/files?path=` | Liste le contenu d'un dossier |
| GET | `/api/progress?path=` | Lit la progression d'un fichier |
| POST | `/api/progress?path=` | Sauvegarde `{position, duration}` |
| DELETE | `/api/files?path=` | Supprime un fichier ou dossier |
| POST | `/api/files/move?path=` | Déplace vers `{destination}` (chemin relatif) |
| POST | `/api/files/mkdir` | Crée un dossier `{path}` |
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
| GET | `/api/stream?path=` | Stream HTTP avec support `Range` (seeking natif) |
| GET | `/api/transcode?path=` | Stream transcodé via ffmpeg |
| POST | `/api/download` | Télécharge une vidéo web via yt-dlp `{url, cookies?, referer?, title?}` |
| POST | `/api/jobs/{job_id}/cancel` | Annule un job de téléchargement en attente ou en cours |
| DELETE | `/api/jobs/{job_id}` | Retire un job terminé/échoué/annulé du store en mémoire |

### Lecture native versus transcodage

Hoard tente aujourd'hui la lecture native en premier en assignant `/api/stream` à l'élément vidéo HTML5. Si le navigateur rejette la source avec `MEDIA_ERR_SRC_NOT_SUPPORTED`, le frontend retente via `/api/transcode`.

BL-019 documente l'étape suivante : passer d'un simple fallback à l'erreur à une décision guidée par les métadonnées afin que Hoard ne privilégie la lecture native que lorsque le navigateur et l'appareil confirment réellement la prise en charge du conteneur et des codecs du fichier. Voir `docs/native-playback.fr.md` pour la matrice de compatibilité et la stratégie de détection recommandée.

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
```

### Initial Sweep

L'initial sweep permet à Hoard de démarrer une **vidéo neuve** à un offset configuré au lieu de `0`.

- Valeur globale par défaut : stockée dans la table `settings` sous la clé `initial_sweep_seconds`
- Surcharge par dossier : stockée dans `initial_sweep_folders`, indexée par chemin relatif de dossier
- La surcharge de dossier gagne sur la valeur globale
- `0` signifie désactivé
- Une progression de lecture déjà sauvegardée gagne toujours sur toute règle d'initial sweep

### Jobs en arrière-plan

Les découpes vidéo (`/api/files/cut`) s'exécutent dans des threads daemon individuels. Les téléchargements web utilisent une file séquentielle :

- **Phase 1 (thread immédiat)** : à l'appel de `POST /api/download`, un thread dédié démarre immédiatement, passe le job en `resolving`, remplit un aperçu du nom de fichier depuis l'indice `title`, puis passe en `pending` et ajoute le job à la `queue.Queue`.
- **Phase 2 (worker de file)** : un seul thread daemon (`dl-worker`) défile les jobs un par un et exécute le téléchargement yt-dlp, évitant la surcharge de bande passante.

**Cycle de vie du statut d'un job :** `pending` → `resolving` → `pending` (avec nom de fichier) → `running` → `done` / `error` / `cancelled`

Tout l'état des jobs est conservé en mémoire dans `_jobs : dict[str, dict]`. Les champs préfixés par `_` sont privés et retirés avant la sérialisation JSON par `_job_for_api()`. L'endpoint `/api/jobs` permet au frontend de poller l'état.

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
