# Hoard — Guide utilisateur

## Présentation

Hoard est un navigateur de fichiers média accessible depuis un navigateur web. Il est conçu pour parcourir un disque réseau (NAS), lire des vidéos, visionner des images et archives BD, lire des fichiers audio et des PDF directement dans le navigateur, et se souvenir de là où tu t'es arrêté.

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
| **✏ Renommer** | Ouvre la fenêtre de renommage (touche `R`) |
| **🗑 Supprimer** | Supprime le fichier après confirmation |

### Déplacer vers un dossier quelconque

Le modal de déplacement propose deux modes :

- **Dossiers épinglés** : déplacement rapide vers un dossier prédéfini.
- **📂 Parcourir…** : ouvre un sélecteur qui parcourt toute l'arborescence pour choisir n'importe quel dossier de destination.

---

## Lecteurs alternatifs

En plus des vidéos, Hoard peut ouvrir directement plusieurs types de fichiers :

### Images

Les fichiers JPG, PNG, GIF, WEBP, BMP, TIFF et AVIF s'ouvrent dans une visionneuse intégrée.

- **← / →** (clavier ou boutons) : image précédente / suivante dans le dossier
- **Bouton ▣** : bascule entre affichage ajusté à la largeur et plein écran
- **✕** : ferme la visionneuse

### Archives BD/manga (.cbz, .zip, .cbr)

Les archives d'images s'ouvrent page à page comme une visionneuse.

- Navigation identique à la visionneuse d'images (← / →)
- La page courante est sauvegardée pour reprendre là où tu t'es arrêté
- `.cbr` nécessite que `unrar-free` soit installé sur le serveur

### PDF

Les fichiers PDF sont rendus directement dans le navigateur via PDF.js.

- **← / →** : page précédente / suivante
- **− / +** : dézoomer / zoomer
- **Bouton ▣** : bascule entre ajustement à la largeur et taille originale
- La page courante est sauvegardée

### Audio (.mp3, .flac, .ogg, .m4a, .aac, .wav, .opus)

Les fichiers audio s'ouvrent dans un lecteur minimaliste.

- Barre de progression cliquable
- Boutons ◀◀ / ▶ / ▶▶ (seek ±10 s, lecture/pause)
- La position est sauvegardée

### Suivi de progression

L'état **vu / en cours / non vu** fonctionne pour tous les types de médias, pas seulement les vidéos. Le pourcentage est calculé sur la même base (position / durée pour vidéo et audio ; page / total pour PDF et archives).

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

> À la première ouverture d'une vidéo sur un appareil tactile, un court écran d'aide présente les principaux gestes. Touchez **Compris** pour le fermer ; il ne réapparaît plus ensuite.

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
| `↑ / ↓` *(sans média)* | Déplacer le curseur dans la liste |
| `↑ / ↓` *(média en cours)* | Volume +/− 10 % |
| `Entrée` | Ouvrir l'élément sous le curseur |
| `Espace` | Lecture / Pause |
| `← / →` | Seek court (10 s par défaut) |
| `Shift + ← / →` | Seek moyen (30 s par défaut) |
| `Ctrl + ← / →` | Seek long (60 s par défaut) |
| `Alt + ← / →` | Seek très long (120 s par défaut) |
| `F` | Plein écran (fenêtré dans le navigateur sur PC) |
| `Maj + F` | Vrai plein écran de l'OS (sur PC ; sinon `F11`) |
| `Échap` | Quitter le plein écran → fermer le player → remonter d'un cran dans l'arborescence |
| `M` | Muet / Son |
| `C` | Sous-titres (cycle des pistes / désactivé) |
| `[ / ]` | Vitesse − / + (0,5× → 1× → 1,5× → 2×) |
| `A` | Cycle aspect ratio (Fit / Fill / …) |
| `W` | Marquer vu / non vu |
| `PageDown / PageUp` | Vidéo suivante / précédente dans le dossier |
| `I / O` | Marquer point IN / OUT |
| `E` | Ouvrir la fenêtre Couper |
| `D` | Ouvrir la fenêtre Déplacer |
| `R` | Renommer (fichier en cours ou élément sélectionné) |
| `Suppr` | Supprimer le fichier en cours |
| `S` | Sauvegarder la position initiale du dossier |
| `?` | Afficher / masquer l'aide clavier |

---

## Manette / Gamepad

Hoard supporte les manettes de jeu via la **Gamepad API** du navigateur (Xbox, PlayStation DualSense, Switch Pro, Steam Deck, iPhone avec manette Bluetooth, etc.).

### Connexion

- Connecte la manette (USB ou Bluetooth) et appuie sur un bouton dans Hoard.
- Un toast « 🎮 Manette connectée » confirme la détection.
- **Steam Deck / Firefox** : Firefox n'envoie l'événement `gamepadconnected` qu'après un appui. Un toast « Appuyez sur un bouton pour activer la manette » apparaît si la manette est détectée mais pas encore active.

### Actions — Lecteur vidéo

| Bouton | Base | + L1 | + R1 | + L1+R1 |
|--------|------|------|------|---------|
| **A** | Lecture / Pause | Sous-titres | Déplacer → Dossier 1 | Aller à 0% |
| **B** | Fermer le lecteur | — | Déplacer → Dossier 2 | — |
| **X** | Marquer vu / non vu | Ratio image | Déplacer → Dossier 3 | Aller à 50% |
| **Y** | Plein écran | Aller à 0% | — | Aller à 100% |
| **D-pad ←/→** | Seek moyen | Seek long | Seek très long | — |
| **D-pad ↑/↓** | Volume ±10% | Fichier précédent/suivant | Aller à 25%/75% | — |
| **Select** | Paramètres | — | — | — |
| **Start** | Afficher la carte des boutons | — | — | — |
| **L3** (clic stick) | Muet / Son | — | — | — |
| **R3** (clic stick) | Cycle vitesse (0,5× → 1× → 1,5× → 2× → …) | — | — | — |
| **Stick gauche X** | Scrubbing analogique | — | — | — |
| **Stick droit Y** | Volume analogique | — | — | — |

### Actions — Navigateur de fichiers (sans vidéo)

| Bouton | Action |
|--------|--------|
| **D-pad ↑/↓** | Déplacer le curseur dans la liste |
| **Stick gauche Y** | Déplacer le curseur (analogique) |
| **A** | Ouvrir le fichier ou dossier sélectionné |
| **B** | Remonter d'un niveau |
| **Start** | Ouvrir les Paramètres |

### Modificateurs (L1 / R1)

Maintenir **L1** ou **R1** active une couche de commandes supplémentaires. Les deux ensemble (L1+R1) activent une quatrième couche. Un **badge en coin** (ex : « 🎮 L1 ») indique la couche active.

### Carte des boutons

Appuie sur **Start** (ou le bouton « Afficher la carte des boutons » dans Paramètres) pour afficher un overlay listant toutes les actions disponibles par couche, mis à jour dynamiquement avec les durées de seek configurées.

### Paramètres manette

Dans **Paramètres → 🎮 Manette** :

| Paramètre | Description |
|-----------|-------------|
| **Manette activée** | Active / désactive complètement la détection gamepad |
| **Retour haptique** | Vibration courte sur play/pause, seek, vu/non vu (Chrome uniquement) |
| **Zone morte** | Seuil de détection des sticks (défaut 20%). Augmenter si les sticks dérivent. |

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
| **Activer le transcodage** | Quand désactivé, Hoard envoie toujours le fichier original (`/api/file`) sans appeler le transcodeur. Utile si votre NAS est lent ou si votre navigateur lit nativement le format. |
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
