# Hoard — Guide d'installation

## Prérequis

| Méthode | Prérequis |
|---------|-----------|
| Local (Python) | Python 3.12+, pip, ffmpeg (pour la découpe vidéo et les téléchargements) |
| Docker | Docker Engine 24+, Docker Compose v2 |
| Synology NAS | DSM 7+, paquet Docker ou Container Manager |

> **Note :** `yt-dlp` est installé automatiquement comme dépendance Python (`requirements.txt`). `ffmpeg` doit être disponible dans le PATH système pour la découpe vidéo et la fusion audio/vidéo lors des téléchargements. L'image Docker inclut les deux.

---

## 1. Installation locale (Python)

### Cloner le dépôt

```bash
git clone https://github.com/davidp57/hoard.git
cd hoard
```

### Créer l'environnement virtuel et installer les dépendances

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements-dev.txt
```

### Lancer l'application

```bash
# Variables d'environnement requises
export MEDIA_ROOT=/chemin/vers/tes/videos   # dossier à parcourir
export DB_PATH=/tmp/hoard.db                # base SQLite
export PREDEFINED_FOLDERS="Vu,A revoir"    # dossiers rapides (optionnel)

uvicorn backend.main:app --reload --port 8000
```

Sur Windows PowerShell, remplace `export` par `$env:` :

```powershell
$env:MEDIA_ROOT = "C:\Videos"
$env:DB_PATH = "$env:TEMP\hoard.db"
uvicorn backend.main:app --reload --port 8000
```

Ouvre `http://localhost:8000` dans ton navigateur.

---

## 2. Docker (développement local)

### Préparer le dossier média

```bash
mkdir dev-media
# Copie quelques fichiers vidéo dans dev-media/ pour tester
```

### Lancer avec hot-reload

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Le backend se recharge automatiquement à chaque modification de `backend/main.py`.  
Pour pointer vers un dossier médias externe :

```bash
LOCAL_MEDIA_PATH=/chemin/absolu/vers/videos \
  docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

---

## 3. Déploiement production (Synology NAS)

### Copier les fichiers sur le NAS

Via SSH ou l'explorateur de fichiers DSM, copie le contenu du dépôt dans :

```
/volume1/docker/hoard/
```

### Adapter docker-compose.yml

Ouvre `docker-compose.yml` et ajuste le volume des médias :

```yaml
volumes:
  - /volume1/downloads:/media:rw   # adapte ce chemin
  - hoard_data:/data
```

### Démarrer le container

```bash
# Sur le NAS, via SSH
cd /volume1/docker/hoard
docker compose up -d --build
```

L'application est accessible sur `http://IP_DU_NAS:8000`.

### Mise à jour

```bash
docker compose pull
docker compose up -d
```

---

## 4. Configuration

Toute la configuration passe par des **variables d'environnement** dans `docker-compose.yml` (section `environment`) ou au lancement du serveur.

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `MEDIA_ROOT` | `/media` | Chemin racine des médias dans le container |
| `DB_PATH` | `/data/progress.db` | Fichier SQLite de suivi de progression |
| `PREDEFINED_FOLDERS` | `Vu,A revoir,A supprimer` | Dossiers rapides (séparés par des virgules) |

### Exemple avec Portainer

Dans l'interface Portainer, crée un stack avec le contenu de `docker-compose.yml` et ajoute / modifie les variables d'environnement selon ton setup.

---

## 5. Reverse proxy (accès externe)

Pour exposer Hoard via un sous-domaine (ex. `hoard.monnas.me`), utilise le reverse proxy intégré de DSM :

1. **Panneau de configuration → Portail de connexion → Reverse Proxy**
2. Ajoute une règle :
   - Source : `hoard.monnas.me:443` (HTTPS)
   - Destination : `localhost:8000`

> **Attention :** si tu exposes l'application hors du LAN, active une authentification (cf. feuille de route v2.0).

---

## 6. Persistance des données

La base SQLite (`progress.db`) stocke la progression de lecture de tous les fichiers. Elle est montée dans un volume Docker nommé (`hoard_data`) pour survivre aux mises à jour du container.

Pour sauvegarder / exporter la base :

```bash
docker run --rm \
  -v hoard_data:/data \
  -v $(pwd):/backup \
  alpine cp /data/progress.db /backup/progress.db.bak
```
