# Changelog utilisateur — Hoard 🐦

Journal des changements visibles par l'utilisateur, sans jargon technique.

---

## [Non publié]

### Corrections
- **Aide clavier lisible** : la fenêtre d'aide (touche `?`) s'affichait en texte sombre sur fond sombre sur PC/Firefox. Elle est de nouveau parfaitement lisible.

### Améliorations
- **Plein écran plus souple sur PC** : la touche `F` (et le bouton plein écran) affiche maintenant la vidéo en plein cadre **dans la fenêtre du navigateur** (interface masquée), sans passer en plein écran système. Pour un vrai plein écran, utilise `Maj+F` (ou `F11`). Sur iPad/tablette, rien ne change.
- **Touche Échap plus pratique** : sur PC, quand aucune vidéo n'est ouverte, `Échap` remonte d'un dossier dans l'arborescence (comme le bouton B de la manette).

### Nouveautés
- **Galeries d'images** : un dossier rempli d'images (BD, scan, lot de photos) s'ouvre maintenant comme un **album** unique — la première image s'affiche directement et tu fais défiler les pages, au lieu de voir la liste des fichiers. Hoard se souvient de la page où tu t'es arrêté, et l'album affiche son avancement dans la liste (comme une vidéo). Une **barre de miniatures** permet de sauter directement à une image ; à la souris, survole une miniature pour la supprimer (✕) ou la déplacer (›). Les archives BD (.cbz/.zip/.cbr) fonctionnent de la même façon. Un PDF ou un texte glissé dans le dossier reste visible dans l'album avec un aperçu.
- **Sous-titres** : si un fichier `.srt` ou `.ass` porte le même nom que ta vidéo (dans le même dossier), Hoard le détecte automatiquement. Active/désactive les sous-titres avec le bouton 💬, la touche `C` ou la manette. (Les `.ass` sont affichés en texte simple, sans mise en forme.)
- **Renommer fichiers et dossiers** : un bouton ✏ apparaît sur chaque élément de la liste (ou appuie sur `R`) pour le renommer directement depuis Hoard, sans passer par un autre outil. Renommer un dossier conserve la progression de lecture des vidéos qu'il contient.
- **Trier par taille ou par état** : en plus de Date et Nom, tu peux désormais trier la liste par taille de fichier ou par état de lecture (non vu / en cours / vu).
- **Aide aux gestes tactiles** : la première fois que vous ouvrez une vidéo sur un écran tactile, un petit guide montre les gestes disponibles (double-tap pour avancer/reculer, tap pour mettre en pause, glissé pour le volume et la luminosité). Il ne s'affiche qu'une seule fois.

### Améliorations
- **Accessibilité** : les boutons icône (accueil, réglages, lecture/pause, plein écran…) ont désormais un libellé pour les lecteurs d'écran, la navigation au clavier affiche un contour de focus visible, et le texte gris secondaire est plus contrasté donc plus lisible.
- **Retour en cas de problème réseau** : si le serveur est lent à répondre (par ex. NAS en veille) ou injoignable, l'application affiche maintenant un message au lieu de rester figée. Les actions concernées : navigation, recherche, reprise de lecture, déplacement et suppression.

### Sécurité
- **Protection par mot de passe (optionnelle)** : il est désormais possible d'exiger un identifiant et un mot de passe pour accéder à Hoard, pratique si vous l'exposez sur Internet. Cette option s'active lors de l'installation (variables `HOARD_AUTH_USER` / `HOARD_AUTH_PASS`) et reste désactivée par défaut.
- **Code PIN mieux protégé** : le code PIN est maintenant stocké de façon beaucoup plus sûre (hachage salé). Votre PIN existant continue de fonctionner sans rien changer.
- **Réglages — chemin du fichier de cookies** : le chemin saisi pour les cookies de téléchargement est maintenant vérifié au moment de l'enregistrement (il doit s'agir d'un fichier `.txt` existant et lisible). Un message clair s'affiche si le chemin est invalide.

---

## [v2.2.0] — 2026-05-20

### Nouveautés
- **Navigation clavier enrichie** : les touches ↑/↓ déplacent le curseur dans la liste quand aucun média n'est actif, et ajustent le volume pendant la lecture. `Entrée` ouvre l'élément sélectionné. `W` bascule l'état vu/non vu. `[` et `]` diminuent ou augmentent la vitesse de lecture (style VLC : 0,5× → 1× → 1,5× → 2×). `Échap` quitte d'abord le plein écran, puis ferme le player.
- **Manette — L3 / R3** : cliquer le stick gauche (L3) coupe/rétablit le son ; cliquer le stick droit (R3) cycle la vitesse de lecture.
- **Visionneuse d'images** : les photos (JPG, PNG, GIF, WEBP, AVIF…) s'ouvrent directement dans l'interface. Navigation avec les flèches ← / →, bascule entre affichage ajusté et pleine largeur.
- **Lecteur d'archives BD/manga** : les fichiers `.cbz`, `.zip` et `.cbr` s'ouvrent page à page comme une visionneuse d'images.
- **Lecteur PDF** : les fichiers PDF s'affichent directement, avec navigation page à page et contrôles de zoom.
- **Lecteur audio** : les fichiers audio (MP3, FLAC, OGG, M4A, WAV…) se lisent dans un player simplifié avec barre de progression.
- **Suivi de progression universel** : l'état vu/en cours/non vu est maintenant disponible pour les images, PDF, archives et fichiers audio, pas seulement pour les vidéos.
- **Diagramme interactif de la manette Xbox** : l'overlay d'aide (bouton Start) affiche maintenant un diagramme annoté de la manette avec mise en évidence dynamique des couches LB/RB en temps réel.
- **Navigation clavier dans les dialogues** : dans les fenêtres de suppression, déplacement et export, utilisez ↑/↓ pour naviguer entre les options, Entrée pour valider et Échap pour annuler.
- **Aide raccourcis clavier (`?`)** : appuyez sur `?` à tout moment pour afficher/masquer un tableau de tous les raccourcis clavier.
- **D-pad en maintien** : maintenir une direction du D-pad dans la liste de fichiers provoque un défilement continu rapide (400 ms délai initial, répétition 100 ms).
- **Bouton Rafraîchir (↻)** : un bouton `↻` dans la barre de tri remplace le rafraîchissement automatique de 30 secondes. La liste se met à jour à la demande, et toujours automatiquement après une suppression, un déplacement ou une découpe.

### Corrections
- **Transcodage désactivé ignoré** : le player ne respectait pas l'option « Transcodage activé » désactivée dans les Paramètres. Corrigé — un message informatif s'affiche à la place du basculement automatique.
- **Dialogues d'action invisibles en faux-plein-écran** (manette) : les fenêtres Supprimer, Déplacer et Export étaient masquées derrière la vidéo. Corrigé.
- **Image d'aide manette tronquée** : le diagramme de manette dans l'overlay d'aide (Start) était bloqué à 620 px fixes. Il s'adapte maintenant à 75 % de la fenêtre.
- **Curseur manette perdu après rafraîchissement** : le curseur de navigation ne disparaît plus lors d'un rafraîchissement du même dossier (filtre, tri, action fichier).

---

## [v2.1.0] — 2026-05-15

### Nouveautés
- **Tags sur les fichiers** : ajoutez des étiquettes texte libres à vos fichiers et dossiers (bouton 🏷 dans chaque entrée). Les tags apparaissent comme petits badges dans la liste et un filtre par tag s'affiche automatiquement dans la barre de tri.
- **Choisir n'importe quel dossier de destination** : le bouton « 📂 Parcourir… » dans la fenêtre de déplacement permet de naviguer dans toute l'arborescence pour choisir où déplacer un fichier.
- **Recherche de fichiers** : champ de recherche dans la barre de tri pour trouver rapidement un fichier par son nom (recherche récursive dans le dossier courant).
- **Métadonnées vidéo** : codec, résolution, durée et bitrate s'affichent sous le titre du fichier en cours de lecture.
- **Vitesse de lecture** : bouton de cycle 0.5× / 1× / 1.5× / 2× dans les contrôles.
- **Rafraîchissement automatique** : la liste de fichiers se met à jour toutes les 30 secondes quand vous n'êtes pas en train de regarder une vidéo.
- **Dossiers home multiples** : possibilité de définir plusieurs racines de navigation.
- **Racine de démarrage par défaut** : désignez une racine comme point d'entrée par défaut — l'app y navigue directement au lancement et après saisie du PIN, sans passer par le sélecteur. Changez la racine par défaut depuis Paramètres → Racines (bouton ⌂ sur chaque racine non-défaut). Ajouter une nouvelle racine ouvre désormais un sélecteur de dossier au lieu d'utiliser silencieusement le dossier courant.
- **Support manette / gamepad** : Hoard reconnaît désormais les manettes Xbox, Switch Pro, DualSense, Steam Deck et tout contrôleur Bluetooth compatible. Contrôles en lecture : A (play/pause), B (fermer), X (marquer vu), Y (plein écran), D-pad ←/→ (seek), D-pad ↑/↓ (volume), L1 / R1 comme modificateurs pour les sauts longs et les actions avancées. Navigation dans la liste au D-pad. Stick gauche pour le scrubbing, stick droit pour le volume. Un badge en coin indique la couche active (L1/R1), Start affiche la carte de tous les raccourcis. Activation, zone morte et retour haptique configurables dans Paramètres → 🎮 Manette.

- **4 niveaux de seek configurables** : les boutons de saut, les raccourcis clavier, les swipes et les double-taps utilisent désormais quatre durées réglables dans les Paramètres (court, moyen, long, très long — 10 s / 30 s / 60 s / 120 s par défaut).
- **Raccourcis clavier étendus** : Shift+← / → (seek moyen), Ctrl+← / → (seek long), Alt+← / → (seek très long), A (aspect ratio), PageDown / PageUp (vidéo suivante/précédente), I / O (marqueurs IN/OUT), C (découpe), D (déplacement), Suppr (supprimer), S (position initiale du dossier), ? (aide).
- **Confirmation visuelle de chaque seek** : un toast apparaît après chaque saut (bouton, clavier ou swipe) pour indiquer le delta réel.
- **Modaux compatibles plein écran** : les fenêtres Déplacer, Découper, Supprimer et l'aide clavier restent visibles au-dessus du plein écran natif du navigateur.
- **Contrôles plein écran discrets** : le mouvement de la souris ne révèle les contrôles qu'en bas de l'écran (10 %), pour ne pas déranger pendant la lecture.
- **Option désactiver le transcodage** : nouveau réglage dans Paramètres → Player. Quand il est désactivé, Hoard envoie toujours le flux original sans transcodage — utile si votre NAS est lent ou si votre navigateur lit nativement le format.
- **Zoom barre de progression en plein écran** : la taille de la fenêtre de zoom sur la barre de progression (visible en plein écran) est maintenant réglable dans Paramètres → 🎬 Player (« Zoom barre plein écran »). Valeur par défaut : 20 %, de 5 % à 50 %.
- **Indicateur de volume (OSD)** : une barre de volume apparaît en bas à droite du player quand vous modifiez le volume (touches ↑/↓, manette, swipe). Elle affiche l'icône 🔇/🔉/🔊, un niveau visuel et le pourcentage, puis disparaît après 2,5 secondes.
- **Indicateur de progression en plein écran** : l'affichage de position (coin haut droit) montre le temps restant, une barre de progression globale et une barre zoomée qui indique visuellement où vous en êtes dans le fichier.
- **Lecture automatique du fichier suivant** : après une suppression, un déplacement ou une découpe du fichier en cours de lecture en mode plein écran, le fichier suivant démarre automatiquement et le plein écran est réactivé.
- **Découpe multi-segments** : le système de découpe passe à plusieurs segments indépendants. Marquez autant de paires IN/OUT que souhaité avec `I` et `O` (manette : `L1+Y` et `R1+Y`). Les segments validés apparaissent en couleur sur la seekbar. Le bouton `✂ N` ou la touche `E` (`L1+R1+Y` manette) ouvre la modal d'export : choisissez entre exporter les segments séparément ou fusionnés en un seul fichier, indiquez le dossier de destination et optionnellement conservez l'original.

### Corrections
- **Manette — plein écran sous Firefox** : le bouton Y fonctionne désormais pour basculer en plein écran sous Firefox PC (bascule sur le mode plein écran CSS en cas de restriction navigateur).
- **Manette — dialogues en plein écran** : les fenêtres Supprimer et Déplacer sont maintenant visibles et utilisables à la manette en mode plein écran natif (SteamDeck, Edge).
- **Manette — curseur de navigation perdu** : supprimer, déplacer ou découper un fichier ne remet plus le curseur au début de la liste. La position est mémorisée et restaurée après l'action.
- **Manette — vidéo fantôme** : une pression rapide sur A après confirmation d'une action ne déclenche plus la lecture d'une vidéo en arrière-plan.
- **Volume — slider non synchronisé** : le curseur de volume se met désormais à jour correctement quelle que soit la façon dont le volume est modifié (manette, swipe tactile, clavier).

---

## [v2.0.0] — 2026-04-06

### Nouveautés
- Téléchargement vidéo depuis une URL web (YouTube, etc.) via un bookmarklet ou un champ de saisie direct.
- File d'attente de téléchargements séquentiels avec suivi en temps réel.
- Accès sécurisé en HTTPS natif (configurable via certificat).

---

## [v1.0.0] — 2026-04-05

### Nouveautés
- Navigation dans les dossiers de votre NAS depuis un navigateur web.
- Indicateurs visuels d'état de lecture : non vu, en cours (barre + %), vu.
- Lecteur vidéo intégré avec gestes tactiles, raccourcis clavier et reprise automatique.
- Déplacement de fichiers vers des dossiers prédéfinis.
- Suppression de fichiers avec confirmation.
- Application web installable (PWA) sur iPad et laptop.
