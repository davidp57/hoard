# Hoard

**Navigateur de fichiers vidéo avec suivi de progression, conçu pour un NAS Synology.**  
**Web video file browser with watch-progress tracking, designed for a Synology NAS.**

[![CI](https://github.com/davidp57/hoard/actions/workflows/ci.yml/badge.svg)](https://github.com/davidp57/hoard/actions/workflows/ci.yml)
[![Docker](https://github.com/davidp57/hoard/actions/workflows/docker-build.yml/badge.svg)](https://github.com/davidp57/hoard/actions/workflows/docker-build.yml)

---

## 🇫🇷 Français

Hoard remplace un lecteur vidéo mobile sur NAS. Il comble un besoin que Jellyfin, Plex ou Kodi ne couvrent pas : parcourir un **filesystem brut**, voir l'état de lecture de chaque fichier, et gérer les fichiers (déplacer, supprimer) — le tout dans une interface web accessible depuis n'importe quel appareil : iPad, laptop, PC de bureau.

### Fonctionnalités

- 📁 Browser de filesystem brut (pas de bibliothèque, pas de métadonnées)
- 🎬 Player HTML5 intégré avec seekbar et contrôles
- 💾 Sauvegarde de position automatique toutes les 5 s, reprise à l'ouverture
- 🟡 État de lecture visible dans la liste : **non vu** / **en cours** (% + barre) / **vu** (≥ 90 %)
- 📌 Dossiers rapides épinglables pour déplacement en 2 taps
- ✂ Découpe vidéo intégrée (via ffmpeg)
- � **Téléchargement de vidéos web** via bookmarklet + yt-dlp : envoie n'importe quelle vidéo en ligne directement sur le NAS depuis n'importe quel onglet, sans quitter la page
- �👆 Gestes tactiles : seek, volume, luminosité, double-tap zones
- ⌨ Raccourcis clavier
- 📱 Responsive : vue divisée desktop, overlay plein écran mobile

### Documentation

| | Français | English |
|---|---|---|
| **Prise en main** | [docs/getting-started.fr.md](docs/getting-started.fr.md) | [docs/getting-started.en.md](docs/getting-started.en.md) |
| **Guide utilisateur** | [docs/user-guide.fr.md](docs/user-guide.fr.md) | [docs/user-guide.en.md](docs/user-guide.en.md) |
| **Installation** | [docs/installation.fr.md](docs/installation.fr.md) | [docs/installation.en.md](docs/installation.en.md) |
| **Développeur** | [docs/developer.fr.md](docs/developer.fr.md) | [docs/developer.en.md](docs/developer.en.md) |

### Démarrage rapide

```bash
git clone https://github.com/davidp57/hoard.git && cd hoard
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements-dev.txt
$env:MEDIA_ROOT = "C:\Videos" ; uvicorn backend.main:app --port 8000
# → http://localhost:8000
```

Ou avec Docker :

```bash
docker compose up -d
# → http://NAS_IP:8000
```

---

## 🇬🇧 English

Hoard is a web video player and file manager for a NAS. It fills a gap that Jellyfin, Plex, and Kodi do not cover: browsing a **raw filesystem**, seeing the watch status of each file, and managing files (move, delete) — all in a web interface accessible from any device: iPad, laptop, or desktop browser.

### Features

- 📁 Raw filesystem browser (no library, no metadata indexing)
- 🎬 Integrated HTML5 player with seekbar and controls
- 💾 Auto-save position every 5 s, auto-resume on re-open
- 🟡 Watch status visible in the list: **unseen** / **in progress** (% + bar) / **watched** (≥ 90 %)
- 📌 Pinnable quick folders for two-tap moves
- ✂ Built-in video trim (via ffmpeg)
- � **Web video download** via bookmarklet + yt-dlp: send any online video directly to the NAS from any browser tab, without leaving the page
- �👆 Touch gestures: seek, volume, brightness, double-tap zones
- ⌨ Keyboard shortcuts
- 📱 Responsive: split-view on desktop, full-screen overlay on mobile

### Documentation

| | Français | English |
|---|---|---|
| **Getting started** | [docs/getting-started.fr.md](docs/getting-started.fr.md) | [docs/getting-started.en.md](docs/getting-started.en.md) |
| **User guide** | [docs/user-guide.fr.md](docs/user-guide.fr.md) | [docs/user-guide.en.md](docs/user-guide.en.md) |
| **Installation** | [docs/installation.fr.md](docs/installation.fr.md) | [docs/installation.en.md](docs/installation.en.md) |
| **Developer** | [docs/developer.fr.md](docs/developer.fr.md) | [docs/developer.en.md](docs/developer.en.md) |

### Quick start

```bash
git clone https://github.com/davidp57/hoard.git && cd hoard
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
MEDIA_ROOT=/path/to/videos uvicorn backend.main:app --port 8000
# → http://localhost:8000
```

Or with Docker:

```bash
docker compose up -d
# → http://NAS_IP:8000
```

---

## Stack

`Python 3.12` · `FastAPI` · `SQLite` · `ffmpeg` · `Vanilla JS` · `Docker`

## License

MIT
