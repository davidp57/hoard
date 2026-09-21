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
| `SSL_CERTFILE` | *(non défini)* | Chemin vers un fichier de certificat PEM. Active le HTTPS natif — sans reverse proxy. |
| `SSL_KEYFILE` | *(non défini)* | Chemin vers la clé privée PEM correspondante. |
| `HOARD_AUTH_USER` / `HOARD_AUTH_PASS` | *(non défini)* | Définir les deux impose une authentification sur chaque requête. Recommandé pour exposer Hoard hors du LAN. Utiliser HTTPS pour ne pas transmettre les identifiants en clair. |
| `HOARD_SECRET_KEY` | *(générée)* | Clé qui signe le cookie de session. Sans elle, une clé est créée au premier démarrage et rangée en base : une installation neuve marche sans rien configurer. La définir donne le moyen de révoquer — changer la valeur invalide toutes les sessions, sur tous les appareils, d'un coup. |
| `HOARD_COOKIE_SECURE` | `1` | Indique si le cookie de session porte `Secure` (HTTPS uniquement). À laisser à `1` en production. Ne passer à `0` que pour joindre une instance de développement en HTTP depuis une autre machine — les navigateurs considèrent déjà `localhost` comme sûr, donc le développement local n'a rien à changer. |
| `LOG_LEVEL` | `INFO` | Niveau de journalisation (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `LOG_DIR` | `<dossier de DB_PATH>/logs` | Dossier des fichiers de log. Chaîne vide = journalisation fichier désactivée (sortie standard uniquement). |
| `LOG_RETENTION_DAYS` | `30` | Nombre de fichiers quotidiens conservés (rotation à minuit). |
| `RESTART_SUPERVISED` | *(auto-détecté)* | `0` / `1`. Indique si un superviseur relance le processus après un arrêt. Détecté automatiquement dans un container ; sert uniquement à formuler le message de confirmation du bouton « Redémarrer Hoard ». |
| `JOB_TTL_SECONDS` | `3600` | Durée de conservation en mémoire d'un job terminé. N'affecte pas l'historique des téléchargements, qui est en base. |
| `DOWNLOAD_SOCKET_TIMEOUT` | `30` | Secondes de silence tolérées sur une connexion de téléchargement avant abandon. Évite qu'un serveur muet immobilise la file (séquentielle). |

### Authentification — à lire avant d'exposer Hoard

**Hoard n'a aucune authentification tant que tu ne l'actives pas.** Par défaut,
toutes les routes sont ouvertes à qui peut joindre le port : lister et lire
toute l'arborescence média, supprimer et déplacer des fichiers, lancer des
téléchargements arbitraires sur le NAS, redémarrer le container, modifier les
réglages.

C'est un choix raisonnable sur un réseau local. Ça ne l'est pas derrière un
reverse proxy avec un nom de domaine public.

Le code PIN des paramètres **ne couvre pas ça** : il verrouille l'interface web,
et aucune route de l'API ne le vérifie. Tout ce qui parle directement à l'API
passe à travers.

Définis les deux variables pour exiger une authentification HTTP Basic sur
chaque requête :

```yaml
environment:
  - HOARD_AUTH_USER=david
  - HOARD_AUTH_PASS=nT8vQ2xK9mR4wL7pZ1sB3dF6
```

Génère le mot de passe plutôt que de l'inventer :

```bash
openssl rand -base64 24
```

Deux pièges :

- **Pas de guillemets.** Sous cette forme de liste, `docker-compose` garde les
  guillemets dans la valeur : `HOARD_AUTH_PASS="abc"` donne un mot de passe de
  cinq caractères, guillemets compris.
- **HTTPS obligatoire.** Le Basic envoie le mot de passe à chaque requête,
  simplement encodé en base64. Active le HTTPS ci-dessous, ou termine le TLS
  sur ton reverse proxy.

Hoard affiche son état d'authentification à chaque démarrage, vérifiable dans
le journal du container :

```
Auth: HTTP Basic enabled for user 'david'
Auth: DISABLED — every endpoint is open, including file deletion and moves. …
```

`/healthz` reste joignable sans identifiants — le contrôle de santé du
container en a besoin — et ne répond rien d'autre que `{"status": "ok"}`.

### Activer le HTTPS

Pour servir Hoard en HTTPS sans reverse proxy, génère un certificat et définis les deux variables :

```bash
# Certificat auto-signé (valide 10 ans)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
  -days 3650 -nodes -subj "/CN=nas.local"
```

Ou utilise [mkcert](https://github.com/FiloSottile/mkcert) pour un certificat approuvé localement :
```bash
mkcert nas.local
```

Puis dans `docker-compose.yml` :
```yaml
volumes:
  - /chemin/sur/nas/certs:/certs:ro
environment:
  - SSL_CERTFILE=/certs/cert.pem
  - SSL_KEYFILE=/certs/key.pem
```

L'application sera accessible sur `https://IP_DU_NAS:8000`.

Cela active aussi l'installabilité PWA sur les vrais appareils : les service workers et les invites d'installation standalone exigent du HTTPS (ou `localhost` en développement local).

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

La base SQLite (`progress.db`) stocke la progression de lecture de tous les fichiers, ainsi que l'**historique des téléchargements**. Elle est montée dans un volume Docker nommé (`hoard_data`) pour survivre aux mises à jour du container.

### Journaux

Les journaux sont écrits **à la fois** sur la sortie standard (visible dans Portainer) et dans un fichier `hoard.log` placé par défaut à côté de la base — soit `/data/logs/hoard.log` avec la configuration standard, donc **dans le même volume persistant**. Le fichier tourne chaque nuit et **30 jours** sont conservés (`LOG_RETENTION_DAYS`).

Ils sont consultables depuis l'interface : **Paramètres → Maintenance → Journal**. Les journaux contiennent les URL téléchargées et les adresses IP appelantes ; si Hoard est exposé hors du réseau local, protège-le avec `HOARD_AUTH_USER` / `HOARD_AUTH_PASS`.

Pour récupérer les journaux depuis l'hôte :

```bash
docker run --rm -v hoard_data:/data -v $(pwd):/backup alpine cp -r /data/logs /backup/hoard-logs
```

Pour sauvegarder / exporter la base :

```bash
docker run --rm \
  -v hoard_data:/data \
  -v $(pwd):/backup \
  alpine cp /data/progress.db /backup/progress.db.bak
```
