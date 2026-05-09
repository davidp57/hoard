# Hoard — Guide utilisateur

## Présentation

Hoard est un navigateur de fichiers vidéo accessible depuis un navigateur web. Il est conçu pour parcourir un disque réseau (NAS), lire des vidéos directement dans le navigateur et se souvenir de là où tu t'es arrêté.

---

## Interface principale

L'interface est divisée en deux zones :

- **À gauche (ou en plein écran sur mobile) :** le navigateur de fichiers
- **À droite (ou en overlay plein écran sur mobile) :** le player vidéo

### Navigateur de fichiers

Le navigateur affiche le contenu d'un dossier. Un **fil d'Ariane** en haut permet de remonter dans l'arborescence. Le bouton **🏠** ramène à l'écran d'accueil.

### Écran d'accueil et dossiers home

Si aucun dossier home n'est configuré, le navigateur s'ouvre directement sur la racine `MEDIA_ROOT`. Si des dossiers home sont définis (via **Paramètres → Dossiers home**), l'appui sur **🏠** affiche un écran de sélection listant chaque dossier home nommé. Clique sur l'un d'eux pour y naviguer directement.

Chaque fichier ou dossier est affiché avec :

- Son nom
- Une **icône d'état** de lecture (pour les fichiers vidéo) :
  - Fond neutre → **non vu**
  - Fond jaune + barre de progression + pourcentage → **en cours**
  - Fond vert → **vu** (≥ 90 % regardé)

### Recherche

Un champ **🔍** est disponible dans la barre de tri. La recherche est insensible à la casse et récursive dans le dossier courant. Le résultat remplace la liste ; effacer le champ (ou appuyer sur ✕) revient à la navigation normale.

### Tags et filtrage par tag

Chaque fichier ou dossier peut porter des **tags texte libres** (ex : `excellent`, `à finir`). Les tags sont stockés en SQLite et affichés comme badges colorés dans la liste.

| Action | Comment |
|--------|---------|
| Ajouter / retirer un tag | Clique sur le bouton **🏷** à côté de l'entrée |
| Filtrer la liste par tag | Clique sur un badge dans la **barre de filtrage par tag** sous la barre de tri |
| Effacer le filtre | Re-clique sur le même badge ou navigue vers un autre dossier |

La barre de filtrage apparaît automatiquement dès qu'un dossier contient au moins un fichier taggé.
| **▶ Lire** | Ouvre la vidéo dans le player |
| **🏷 Tags** | Ouvre le modal de gestion des tags |
| **📁 Déplacer** | Ouvre le modal de déplacement (dossiers épinglés + sélecteur libre) |
| **🗑 Supprimer** | Supprime le fichier après confirmation |

### Déplacer vers un dossier quelconque

Le modal de déplacement propose deux modes :

- **Dossiers épinglés** : déplacement rapide vers un dossier prédéfini.
- **📂 Parcourir…** : ouvre un sélecteur qui parcourt toute l'arborescence pour choisir n'importe quel dossier de destination.

---

## Player vidéo

### Contrôles

| Élément | Rôle |
|---------|------|
| **Barre de progression** | Indique et contrôle la position dans la vidéo |
| **⏮ / ⏭** | Seek moyen (30 s par défaut, configurable) |
| **◀◀ / ▶▶** | Seek court (10 s par défaut, configurable) |
| **▶ / ⏸** | Lecture / Pause |
| **🔊** | Muet/son |
| **Volume** | Curseur de volume |
| **🐢 / 🐇** | Cycle de vitesse : 0,5× → 1× → 1,5× → 2× (réinitialisé à chaque ouverture) |
| **⛶** | Plein écran |

Quand tu passes en plein écran, Hoard masque automatiquement les contrôles pour maximiser la zone vidéo.

- Sur desktop, bouge la souris ou utilise les raccourcis clavier pour faire réapparaître temporairement les contrôles.
- Sur tactile, seule la zone de tap en bas au centre, près des contrôles, doit afficher ou masquer les contrôles.

### Métadonnées vidéo

Quand un fichier est en cours de lecture, le codec, la résolution, la durée et le bitrate sont affichés sous le titre du fichier (via `ffprobe` côté serveur).

### Reprise automatique

La position est sauvegardée automatiquement toutes les 5 secondes. Lorsque tu ouvres à nouveau un fichier, la lecture reprend là où tu t'es arrêté.

### Détection plus intelligente de la lecture native

Avant de basculer vers le transcodage côté serveur, Hoard vérifie maintenant si le navigateur courant a de bonnes chances de lire le fichier original nativement.

- MP4/H.264/AAC reste la base la plus sûre pour la lecture native.
- Pour les formats plus variables comme HEVC, AV1 ou WebM, Hoard sonde d'abord le support du navigateur quand les métadonnées sont disponibles.
- Si la lecture native n'est pas confirmée, Hoard bascule automatiquement vers le flux transcodé.

### Initial Sweep Pour Les Nouvelles Vidéos

Tu peux configurer un **initial sweep** pour les vidéos qui n'ont **encore aucune progression enregistrée**.

- Une **valeur globale par défaut** est disponible dans **Paramètres → Player**.
- Pendant la lecture, une unique action **départ dossier** permet d'enregistrer la **position actuelle** comme départ par défaut du dossier courant.
- `0` signifie désactivé.
- Une surcharge de dossier prend le pas sur la valeur globale.

Cette règle ne s'applique qu'aux vidéos neuves. Dès qu'un fichier a une progression sauvegardée, Hoard reprend toujours à la vraie position enregistrée.

### Marqueurs IN/OUT (découpe)

Des boutons `[IN` et `OUT]` permettent de définir une zone de lecture restreinte (sans modifier le fichier). Le bouton ✂ lance une découpe physique du fichier via ffmpeg.

### Rafraîchissement automatique de la liste

La liste de fichiers se met à jour toutes les 30 secondes quand l'onglet est visible, la vidéo en pause et aucune recherche active. Cela permet de voir apparaître de nouveaux fichiers sans recharger la page.

---

## Gestes tactiles

Les gestes fonctionnent directement sur l'image vidéo.

### Tap simple

| Zone | Action |
|------|--------|
| Bande centrale étroite (haut) | Lecture / Pause |
| Bande étroite en bas-centre | Afficher / masquer les contrôles en plein écran |

### Double-tap

| Zone | Action |
|------|--------|
| Bord gauche (< 20 % de largeur) | Reculer de 30 s |
| Bord droit — tiers bas | Avancer de seek moyen (30 s par défaut) |
| Bord droit — tiers médian | Avancer de seek long (60 s par défaut) |
| Bord droit — tiers haut | Avancer de seek très long (120 s par défaut) |
| Centre | Plein écran |

### Triple-tap

Toggle entre les modes d'affichage **Fit** (image entière visible) et **Fill** (image recadrée).

### Swipe horizontal

Seek progressif dans la vidéo. La **vitesse dépend de la hauteur du doigt** : un swipe en haut de l'écran est plus rapide qu'en bas.

### Swipe vertical

| Zone horizontale | Action |
|-----------------|--------|
| Bord gauche (< 20 %) | Luminosité de l'image |
| Bord droit (> 80 %) | Volume |

---

## Raccourcis clavier

| Touche | Action |
|--------|--------|
| `Espace` | Lecture / Pause |
| `← / →` | Seek court (10 s par défaut) |
| `Shift + ← / →` | Seek moyen (30 s par défaut) |
| `Ctrl + ← / →` | Seek long (60 s par défaut) |
| `Alt + ← / →` | Seek très long (120 s par défaut) |
| `↑ / ↓` | Volume +/− 10 % |
| `F` | Plein écran |
| `M` | Muet / Son |
| `A` | Cycle aspect ratio (Fit / Fill / …) |
| `PageDown / PageUp` | Vidéo suivante / précédente |
| `I / O` | Marquer point IN / OUT |
| `C` | Ouvrir la fenêtre Couper |
| `D` | Ouvrir la fenêtre Déplacer |
| `Suppr` | Supprimer le fichier en cours |
| `S` | Sauvegarder la position initiale du dossier |
| `?` | Afficher / masquer l'aide clavier |

---

## Dossiers rapides (épingles)

Les **dossiers rapides** permettent de déplacer un fichier vers un dossier fréquemment utilisé en deux taps.

- Clique sur l'icône 📌 à côté d'un dossier pour l'épingler / le désépingler.
- Les dossiers épinglés apparaissent dans le modal de déplacement.

---

## Téléchargement de vidéos

Hoard peut télécharger des vidéos depuis le web via **yt-dlp** et les sauvegarder directement sur le NAS.

### Installer la bookmarklet

1. Ouvre les **Paramètres** (bouton ⚙️ dans l'en-tête).
2. Descends jusqu'à la section **Téléchargements**.
3. **Glisse** le lien « 📥 Télécharger avec Hoard » vers ta barre de favoris.

### Télécharger une vidéo

**Depuis n'importe quelle page web** — clique sur la bookmarklet. Elle soumet le téléchargement **en arrière-plan** et injecte une fenêtre de statut en direct directement dans la page courante — aucune navigation, aucun onglet ouvert. Le dialogue progresse à travers ⌛ « Analyse de l'URL… » → 📥 « Téléchargement… X% » → ✅ « Terminé ! » (fermeture automatique après 4 s). Si la file est occupée, il affiche ⏳ « En attente dans la file… — titre.mp4 » jusqu'à ce qu'un slot se libère. Tu peux annuler le job depuis le dialogue ou depuis le modal de file de téléchargement de Hoard.

> **Détection intelligente de la source vidéo** : si un élément `<video>` est en lecture sur la page, la bookmarklet capture son URL source directe au lieu de l'URL de la page. Cela permet de télécharger depuis des sites où yt-dlp n'a pas d'extracteur dédié (Patreon, lecteurs vidéo custom, embeds BunnyCDN, etc.). Le modal affiche un indicateur 🎬 quand une source directe a été détectée. L'URL de la page d'origine est automatiquement envoyée comme en-tête `Referer` pour que les CDN qui vérifient l'origine acceptent la requête.

**Depuis Hoard directement** — clique sur le bouton **📥** dans l'en-tête, colle l'URL et confirme.

**Indication de nom de fichier** : le champ « Nom du fichier » est pré-rempli avec le titre de la page lors de l'utilisation de la bookmarklet. Tu peux le modifier librement avant de lancer le téléchargement. S'il est laissé vide, yt-dlp extrait le titre automatiquement.

### File de téléchargement

Tous les téléchargements sont regroupés dans une file centrale accessible depuis le bouton **📥** dans l'en-tête :

- Un **badge** sur le bouton indique le nombre de téléchargements actifs.
  - Badge jaune = téléchargements en cours.
  - Badge vert = tous terminés (la file contient des éléments à supprimer).
- Clique sur le bouton pour ouvrir le **modal de file de téléchargement**, qui affiche chaque téléchargement avec son nom, sa barre de progression et son statut.
- Clique sur **✕** à côté d'un téléchargement terminé ou en erreur pour le retirer de la file.
- Clique sur **⏹** sur un téléchargement en attente ou en cours pour l'annuler immédiatement. Tout fichier `.part` partiel laissé par yt-dlp est effacé automatiquement.
- **File séquentielle** : les téléchargements s'exécutent un par un. Les nouveaux jobs attendent à l'état « pending » jusqu'à ce que le téléchargement en cours se termine, évitant la surcharge.
- **Les téléchargements continuent même si tu fermes l'onglet** : ils s'exécutent comme des threads en arrière-plan sur le NAS. Quand tu reviens sur Hoard, le widget de file se reconnecte automatiquement aux jobs en cours.
- **Rafraîchissement automatique** : quand un téléchargement se termine, le navigateur de fichiers se rafraîchit automatiquement si tu parcours le dossier de téléchargement.

### Paramètres

| Paramètre | Description |
|-----------|-------------|
| **Durées de seek** | Quatre niveaux configurables dans **Paramètres → Player** : court (défaut 10 s), moyen (30 s), long (60 s), très long (120 s). Utilisés par les boutons, les raccourcis clavier et les double-taps. |
| **Activer le transcodage** | Quand désactivé, Hoard envoie toujours le flux original (`/api/stream`) sans appeler le transcodeur. Utile si votre NAS est lent ou si votre navigateur lit nativement le format. |
| **Initial sweep par défaut** | Démarre les vidéos neuves à N secondes au lieu de 0. S'applique seulement si le fichier n'a aucune progression enregistrée. `0` le désactive globalement. |
| **Dossiers home** | Liste de dossiers nommés affichés sur l'écran d'accueil. Ajouter/supprimer dans **Paramètres → Dossiers home**. |
| **Dossier de téléchargement** | Dossier cible, relatif à `MEDIA_ROOT` (défaut : `Downloads`). Créé automatiquement s'il n'existe pas. |
| **Chemin du fichier cookies** | Chemin absolu vers un fichier `cookies.txt` au format Netscape. Utile pour les sites qui nécessitent une authentification. |

### À propos des cookies

La bookmarklet transmet le `document.cookie` de la page source. Attention : les **cookies HttpOnly ne sont pas accessibles en JavaScript** — pour les sites qui en ont besoin (ex : plateformes de streaming), exporte un fichier `cookies.txt` avec une extension navigateur et renseigne son chemin dans les paramètres.

---

## Disposition responsive

| Écran | Mode |
|-------|------|
| Largeur > 700 px | Vue divisée : liste à gauche, player à droite |
| Largeur ≤ 700 px | Liste plein écran, player en overlay |

## Installer comme une app

Sur les navigateurs qui prennent en charge l'installation des web apps, Hoard peut maintenant s'installer comme une application autonome au lieu de rester dans un onglet classique. Sur iPad et iPhone, utilise l'action **Ajouter à l'écran d'accueil** du navigateur pour obtenir le même lancement en mode standalone.

Cette couche d'installation ne met en cache que le shell de l'application pour rouvrir l'interface plus vite. Hoard a toujours besoin d'une connexion active au NAS pour les appels API, la navigation dans les dossiers et la lecture vidéo.
