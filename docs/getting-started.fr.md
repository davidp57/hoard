# Hoard — Tutoriel de prise en main

Ce tutoriel te guide pas à pas pour installer Hoard et faire tes premières lectures avec suivi de progression.

---

## Étape 1 — Lancer l'application

### Option A : en local avec Python

```bash
git clone https://github.com/davidp57/hoard.git
cd hoard
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS
pip install -r requirements-dev.txt

# Remplace le chemin par ton dossier vidéos
$env:MEDIA_ROOT = "C:\Videos"   # Windows PowerShell
export MEDIA_ROOT=/home/user/Videos  # Linux / macOS
export DB_PATH=/tmp/hoard.db

uvicorn backend.main:app --port 8000
```

### Option B : avec Docker

```bash
mkdir dev-media
# Copie quelques vidéos dans dev-media/

docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Ouvre `http://localhost:8000` dans ton navigateur.

---

## Étape 2 — Naviguer dans les fichiers

Lorsque l'application s'ouvre, tu vois la **liste des fichiers et dossiers** de ton dossier racine.

- Clique sur un **📁 dossier** pour l'ouvrir.
- Le **fil d'Ariane** en haut te montre où tu es. Clique sur n'importe quel élément pour remonter.
- Le bouton **🏠** à gauche du fil d'Ariane te ramène à la racine.

---

## Étape 3 — Lire une vidéo

Clique sur le **nom d'un fichier vidéo** (ou sur le bouton ▶ qui apparaît au survol).

Le player s'ouvre à droite (ou en plein écran sur mobile). La vidéo démarre automatiquement.

### Contrôles basiques

| Action | Comment |
|--------|---------|
| Pause / Lecture | Clique sur **⏸ / ▶** ou appuie sur `Espace` |
| Avancer / Reculer | Boutons **▶▶ / ◀◀** (±10s) ou touches `←` `→` |
| Volume | Slider ou touches `↑` `↓` |
| Plein écran | Bouton **⛶** ou touche `F` |

---

## Étape 4 — Arrêter et reprendre

Arrête la vidéo à n'importe quel moment (ferme l'onglet, navigue ailleurs, éteins ton écran). La progression est sauvegardée **automatiquement toutes les 5 secondes**.

Quand tu reviens sur ce fichier, la lecture **reprend exactement là où tu t'étais arrêté**.

Dans la liste de fichiers, le fichier s'affiche maintenant avec :
- Un **fond jaune** 
- Une **barre de progression** et un pourcentage

Quand tu atteins ≥ 90 % du fichier, il passe en **fond vert** ( "vu").

---

## Étape 5 — Gestes tactiles (écran tactile ou mobile)

Sur l'image vidéo :

| Geste | Action |
|-------|--------|
| **Tap** au centre | Pause / Lecture |
| **Double-tap** bord gauche | − 30 s |
| **Double-tap** bord droit (bas) | + 30 s |
| **Double-tap** bord droit (milieu) | + 60 s |
| **Double-tap** bord droit (haut) | + 90 s |
| **Swipe horizontal** | Seek progressif (vitesse variable) |
| **Swipe vertical** côté droit | Volume |
| **Swipe vertical** côté gauche | Luminosité |

---

## Étape 6 — Déplacer un fichier

Hoard te permet de déplacer des fichiers vers des **dossiers rapides** que tu auras préalablement épinglés.

### Épingler un dossier

1. Navigue jusqu'au dossier à épingler.
2. Clique sur l'icône **📌** à droite de son nom dans la liste.
3. Le dossier est maintenant disponible comme destination rapide.

### Déplacer un fichier

1. Survole (ou appuie longuement sur) le fichier à déplacer.
2. Clique sur le bouton **📁**.
3. Dans le modal, clique sur le dossier de destination.

---

## Étape 7 — Supprimer un fichier

1. Survole (ou appuie longuement sur) le fichier à supprimer.
2. Clique sur le bouton **🗑**.
3. Confirme la suppression dans le dialogue.

---

## Pour aller plus loin

- [Guide utilisateur complet](user-guide.fr.md) — tous les gestes, raccourcis et fonctionnalités détaillés.
- [Guide d'installation](installation.fr.md) — déploiement sur NAS Synology, configuration avancée.
- [Guide développeur](developer.fr.md) — architecture, API, contribuer au projet.
