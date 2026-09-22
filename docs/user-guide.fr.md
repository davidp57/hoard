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

### Tri de la liste

La barre de tri propose cinq critères, chacun inversable avec le bouton **↓ / ↑** :

| Critère | Ce qu'il classe |
|---------|-----------------|
| **Date** | Date du fichier ou du dossier sur le disque (utile pour voir les nouveautés arrivées) |
| **Nom** | Ordre alphabétique |
| **Taille** | Taille du fichier |
| **État** | Non vu, puis en cours, puis vu |
| **Vu** | Date du dernier visionnage |

Le tri **Vu** répond à « qu'ai-je regardé en dernier ». Un dossier prend la date du média le plus récemment regardé **n'importe où en dessous de lui**, même à plusieurs niveaux de profondeur : reprendre une vidéo enfouie dans un sous-dossier fait remonter tout le dossier parent en tête de liste. Les entrées jamais ouvertes n'ont pas de date de visionnage : elles sont regroupées en fin de liste, classées entre elles par date de fichier.

Le tri est **mémorisé** : le critère et le sens choisis dans la barre sont enregistrés côté serveur et réappliqués à la réouverture de l'application, y compris depuis un autre appareil. **Paramètres → Tri de la liste** affiche le tri en cours et permet de le changer sans passer par la barre.

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

### Un fichier du même nom existe déjà à destination

Hoard ne remplace jamais un fichier sans le demander. Si le dossier de destination
contient déjà un fichier portant le même nom, une fenêtre s'ouvre et propose deux
choix :

- **Écraser** : le fichier déplacé remplace définitivement celui qui s'y trouvait
  et reprend sa place dans la liste — progression, tags et segments suivent le
  fichier déplacé.
- **Annuler** : rien ne bouge.

La fenêtre s'utilise aussi bien à la manette (D-pad ↑/↓ pour choisir, **A** pour
valider, **B** pour annuler) qu'au clavier (↑/↓, `Entrée`, `Échap`). Le curseur
démarre sur **Annuler** : écraser est définitif, ça doit être un choix.

Un **dossier** déjà présent à destination ne peut pas être remplacé — Hoard le
signale et laisse tout en place.

---

## Lecteurs alternatifs

En plus des vidéos, Hoard peut ouvrir directement plusieurs types de fichiers :

### Images

Les fichiers JPG, PNG, GIF, WEBP, BMP, TIFF et AVIF s'ouvrent dans une visionneuse intégrée.

- **← / →** (clavier ou boutons) : image précédente / suivante dans le dossier
- **Bouton ▣** : bascule entre affichage ajusté à la largeur et plein écran
- **✕** : ferme la visionneuse

### Galeries (dossiers d'images)

Un dossier qui contient plusieurs images (plus de 3) et aucune vidéo est traité comme
une **galerie** : il apparaît dans la liste comme un média unique (icône 🖼️, barre de
progression, état vu / en cours / non vu), et l'ouvrir affiche directement la première
image au lieu de la liste des fichiers.

- On lit les images les unes après les autres ; la position est sauvegardée et reprise
  à la réouverture, comme pour une vidéo.
- Une galerie est un seul dossier d'images. Un dossier qui **contient des sous-dossiers** reste navigable et affiche chaque sous-dossier comme sa propre galerie (un dossier d'albums s'ouvre donc comme une liste de galeries, pas comme une seule séquence géante).
- Une **barre de vignettes** sous l'image sert de navigation : clique une vignette pour
  y sauter directement.
- **Zoom** : molette de la souris (zoom centré sur le curseur), clic-glisser pour te
  déplacer, double-clic pour basculer zoom ↔ ajusté. Au clavier : `+` / `-` pour
  zoomer, `0` pour réinitialiser, et les flèches déplacent l'image quand on est zoomé
  (sinon elles passent à l'image précédente / suivante). À la manette : stick gauche
  pour déplacer, stick droit ↕ pour zoomer.
- À la souris (ordinateur), survole une vignette pour faire apparaître ✕ (supprimer
  cette image) et › (déplacer cette image). Au clavier/à la manette, supprimer/déplacer
  agit sur la **galerie entière** (comme un film), et `W` la marque vue / non vue.
- Un fichier non-image égaré dans la galerie (PDF, texte…) reste accessible comme
  **passager** : il garde sa place dans la séquence avec un aperçu.

### Archives BD/manga (.cbz, .zip, .cbr)

Les archives d'images sont aussi des galeries : elles s'ouvrent page à page dans la
même visionneuse, avec la barre de vignettes.

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

L'état peut aussi être **posé à la main**, sans ouvrir le fichier — voir *Marquer vu / non vu sans ouvrir le fichier*.

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

### Vidéos 180° côte à côte (VR)

Une vidéo VR 180° contient deux images accolées, une par œil, chacune déformée pour couvrir un demi-tour d'horizon. Affichée telle quelle, elle est illisible. Le bouton 🥽 du lecteur (ou la touche **V**) redresse l'image et vous laisse regarder autour de vous.

Trois états se succèdent à chaque appui :

| État | Ce que vous voyez | Quand l'utiliser |
|------|-------------------|------------------|
| Désactivé | l'image brute du fichier | vidéo ordinaire |
| **Plat** | une seule vue, redressée, que vous promenez | sur un écran normal — ordinateur, tablette |
| **Côte à côte** | deux vues, une par œil | avec des lunettes XR en mode 3D, qui séparent elles-mêmes les deux images |

Pour regarder autour de vous : **glissez le doigt** sur l'image, **tirez à la souris**, ou maintenez **R2** et poussez le **stick droit** de la manette — sans R2 ce stick règle le volume. La molette de la souris rapproche ou éloigne la vue. **Maj+V** remet le regard au centre.

Tant que le mode VR est actif, le glissement ne fait plus ni avance rapide ni réglage du volume — il sert à regarder. L'avance et le volume restent accessibles au clavier, aux boutons du lecteur et au stick gauche de la manette.

#### Avec des lunettes XR

Le mode côte à côte passe automatiquement en plein écran : c'est le seul affichage qui ait un sens dans des lunettes. Les commandes du lecteur disparaissent pendant ce temps — affichées une seule fois sur une image qui va être coupée en deux, elles tomberaient à moitié dans chaque œil et ne seraient lisibles nulle part. Ce qui sert à piloter, en revanche, est écrit **une fois par œil** et reste donc lisible des deux : les messages du lecteur, le menu **Select** et la carte des boutons. Pilote à la manette ou au clavier ; sortir du mode fait tout revenir.

> **Sauf si l'écran entier est déjà en côte à côte** (voir [Toute l'interface en côte à côte](#toute-linterface-en-côte-à-côte) plus bas) : chaque moitié montre alors une image entière, donc la barre du lecteur, la bulle de volume et l'afficheur du temps restent là, en un exemplaire par œil. Tu gardes la position dans le fichier sous les yeux, ce qui n'est pas le cas autrement.

Deux réglages selon ce que font tes lunettes :

- **Image étirée ou non** (touche **B** au clavier, **L2** à la manette, ou le menu de la manette). **Par défaut Hoard le devine** à la forme de l'image : pour obtenir la 3D, des lunettes comme les Viture Beast demandent une sortie deux fois plus large que la normale — du 3840×1080 — et sur une image de cette forme chaque moitié est déjà aux bonnes proportions, donc rien n'est réétiré. Sur un affichage ordinaire, à l'inverse, chaque moitié est réétirée sur toute la largeur. Hoard annonce ce qu'il a deviné par un message au moment où le mode s'active. Si l'image te paraît quand même écrasée ou étirée du double en hauteur, change le réglage — l'effet se voit immédiatement, et ton choix l'emporte toujours sur la devinette. Le raccourci fait le tour des trois états : automatique, étirée, non étirée.
- **Convergence** (**R2 + stick gauche ←/→**, le D-pad pour le pas à pas, ou le menu de la manette). C'est l'angle dont on écarte ou rapproche les deux points de vue : ça change la distance à laquelle ton cerveau place la scène. À laisser à zéro, où les deux images sont exactement telles que les caméras les ont prises — ce qui est correct pour un fichier bien tourné. Si un fichier particulier te fatigue les yeux, c'est qu'il a été tourné avec un écartement de caméras qui ne te va pas, ou remonté de travers. Le stick est proportionnel : une pichenette ajuste, une poussée à fond traverse la plage en deux secondes. **Plus le champ de vision est serré, plus il faut corriger** — l'image est plus agrandie, donc le désalignement aussi. La plage va jusqu'à ±8°, assez pour que ce soit ton œil qui décide et non la borne. **La valeur est retenue pour ce fichier-là**, pas pour les autres : la gêne vient du tournage, un fichier mal monté ne doit pas contaminer le reste.

#### Régler la vue à la manette

Tout se règle en **maintenant R2**, sans rien ouvrir : l'image change pendant que tu règles, ce qui est le seul moyen de juger.

| R2 maintenu | Effet |
|---|---|
| **Stick gauche ↕** | Zoom |
| **Stick gauche ↔** | Convergence (proportionnelle) |
| **D-pad ←/→** | Convergence, pas à pas |
| **Clic stick gauche** | Remettre le zoom |
| **Clic stick droit** | Recentrer le regard |
| **Stick droit** | Regarder autour |

Tant que R2 est maintenu, les autres boutons ne font rien : la manette pilote la vue et rien d'autre. **Relâche R2** et les sticks font exactement ce qu'ils font sur un écran plat, en pleine lecture VR comme ailleurs : l'avance/recul fin, le volume et la vitesse de lecture (**R3**), chacun là où ton réglage d'inversion des sticks les place. Au clavier, **Maj+V** remet d'un coup le regard et le zoom.

#### Reconnaissance et mémorisation

Un fichier VR se signale par un 🥽 dans la liste. Hoard le devine de deux façons : par le nom (les studios y mettent presque toujours `LR`, `3dh`, `180x180`, `VR180` ou `SBS`), et par la forme de l'image — deux yeux carrés côte à côte donnent exactement le double de large que de haut. Le nom se lit dès la liste ; la forme, seulement à l'ouverture du fichier.

Reconnaître un fichier **n'active pas** le mode : le bouton 🥽 se met simplement en évidence. Ouvrir un fichier pour vérifier quelque chose ne doit pas te projeter dans une vue de casque.

En revanche, **le mode que tu choisis est retenu pour ce fichier** et appliqué à sa réouverture, y compris depuis une autre machine — le choix fait sur le laptop vaut sur le Deck. Ça marche aussi dans l'autre sens : si Hoard se trompe et marque comme VR un fichier qui ne l'est pas, désactive le mode et il ne reviendra plus sur celui-là.

Enfin, le mode VR est refusé sur une vidéo lue en transcodage : redresser une image que le serveur est déjà en train de recalculer n'aurait pas de sens, et le NAS n'en a pas les moyens.

Les valeurs par défaut (champ de vision, vitesse du regard, image étirée ou non, convergence) se règlent dans **Paramètres → Player**.

> **Ce que votre machine doit pouvoir faire.** Ces fichiers sont souvent très définis (jusqu'à 8K) et encodés en HEVC. Hoard les envoie tels quels, sans les convertir : c'est l'appareil qui regarde qui doit savoir les décoder. Si l'image saccade ou refuse de s'ouvrir, c'est cette limite-là, et non le mode VR.

---

## Toute l'interface en côte à côte

Des lunettes XR en mode 3D coupent l'image en deux **en permanence**, pas seulement pendant une vidéo. Une interface dessinée une seule fois tombe donc à cheval sur la coupure : chaque œil n'en voit qu'une moitié. Et en sortir coûte une dizaine de secondes d'écran noir, parfois des réglages perdus.

Ce mode dessine **toute** l'application deux fois, une par œil : le code PIN, le navigateur, les visionneuses d'images et de PDF, la vidéo, les réglages et les dialogues. Les deux yeux voient **la même image** — ce n'est pas de la 3D, et c'est précisément ce qui la rend lisible et reposante.

### L'allumer et l'éteindre

| Comment | Geste |
|---|---|
| À la manette | **L1 + R1 + Select** — marche partout, y compris sur l'écran du code PIN |
| Au clavier | **Y** (ou **Alt+Y** si le curseur est dans un champ de saisie) |
| Au menu **Select** | ligne *🥽 Écran côte à côte* |
| Aux réglages | **Paramètres → Lunettes XR** |

**Le même geste l'éteint.** L'allumer par erreur sur un écran normal ne t'enferme donc pas dans un écran illisible.

### Un réglage par appareil

Contrairement à tout le reste, ce mode **ne suit pas d'une machine à l'autre** : il est enregistré dans le navigateur qui l'utilise. Le Deck avec les lunettes le garde allumé, le laptop et l'iPad ne le voient jamais. Il survit en revanche à un rechargement de la page, et il est en place avant même l'écran du code PIN.

### Avec une vidéo

Une **vidéo ordinaire** se voit des deux yeux avec **un seul téléchargement et un seul décodage** : l'œil droit reçoit une copie de l'image, pas une seconde lecture.

Une **vidéo 180°** garde tout son relief, et c'est la seule chose de l'écran qui ne soit pas identique dans les deux yeux — normal : ce fichier contient justement deux images différentes, une par œil, et cette différence *est* le relief. Mets le lecteur en **côte à côte** (touche **V**, ou le menu **Select**) et chaque moitié de l'écran reçoit l'œil qui lui revient, en entier.

Un réglage devient sans objet dans ce mode : **Image côte à côte étirée ou non** (touche **B**). Il sert à savoir si tes lunettes réétirent chaque demi-image ; ici chaque œil reçoit déjà une image entière, il n'y a rien à réétirer. La ligne disparaît du menu et la touche te le dit.

### Ce que ça coûte

Il y a deux fois plus d'interface à dessiner, donc la machine travaille davantage — mesuré sur un dossier de 2 000 fichiers, ce qui est un cas extrême. Déplacer le curseur y reste instantané ; changer de tri ou de dossier redessine la liste entière et prend à peu près deux fois le temps habituel. Sur un dossier de taille ordinaire, ça ne se voit pas.

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
| **B** | Fermer le lecteur | — | Déplacer → Dossier 2 | Supprimer le fichier courant |
| **X** | Marquer vu / non vu | Ratio image | Déplacer → Dossier 3 | Déplacer le fichier courant |
| **Y** | Plein écran | Marquer point IN (segment) | Confirmer segment OUT | Ouvrir la fenêtre Exporter |
| **D-pad ←/→** | Seek moyen | Seek long | Seek très long | — |
| **D-pad ↑/↓** | Volume ±10% | Fichier précédent/suivant | Aller à 25%/75% | ↓ : Aller à 100% |
| **Select** | Menu contextuel | — | — | Écran côte à côte (lunettes XR) |
| **Start** | Afficher la carte des boutons | — | — | — |
| **L2** | Image côte à côte : auto / étirée / non (mode VR) | — | — | — |
| **R2** (maintenu) | Couche VR : zoom, convergence, recentrage — voir plus haut | — | — | — |
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
| **X** | Marquer l'entrée sélectionnée vue / non vue |
| **Select** | Ouvrir le **menu contextuel** |
| **Start** | Afficher la carte des boutons |
| **L1+R1+B** | Supprimer l'entrée sélectionnée |
| **L1+R1+X** | Déplacer l'entrée sélectionnée |

### Menu contextuel (Select)

Tout ce que la barre de tri et les boutons de ligne proposent est accessible à la manette par un seul bouton : **Select** ouvre un menu qui liste ce qui s'applique là où tu te trouves. **D-pad** pour parcourir, **A** pour valider, **B** pour fermer.

Le menu comporte deux parties :

- **L'entrée sous le curseur** (si le curseur est posé) — Ouvrir, Marquer vu / non vu, Renommer, Tags, Accès rapide, Déplacer, Supprimer.
- **Le dossier courant** — les cinq critères de tri et le sens, les tags présents dans le dossier pour filtrer, Nouveau dossier, Rafraîchir, Rechercher, Écran d'accueil, Téléchargements, Paramètres, Aide manette.

Ce qui ne s'applique pas à l'entrée n'est pas affiché : « Accès rapide » n'apparaît que sur un dossier, « Marquer vu » que sur un média ou une galerie.

**Select ouvre aussi le menu pendant la lecture**, avec le contenu du lecteur : ⏱ Départ du dossier, Marquer vu / non vu, Sous-titres, Fit/Fill, Vitesse de lecture, Exporter les segments (s'il y en a), Renommer, Tags, Déplacer, Supprimer, Fermer le lecteur, Paramètres et Aide manette. C'est le seul chemin manette vers **⏱ Départ du dossier**, qui n'a pas de bouton dédié.

### Marquer vu / non vu sans ouvrir le fichier

Depuis la liste, **X** ou l'entrée du menu bascule l'état d'un média sans le lire. C'est utile pour un film vu ailleurs, ou pour remettre à zéro une série qu'on veut reprendre.

Marquer **non vu** remet aussi la position de lecture à zéro — un fichier affiché comme non vu ne doit pas reprendre au milieu. Et rouvrir un fichier marqué vu pour le regarder le refait passer « en cours » : c'est la lecture réelle qui a le dernier mot.

### Modificateurs (L1 / R1)

Maintenir **L1** ou **R1** active une couche de commandes supplémentaires. Les deux ensemble (L1+R1) activent une quatrième couche. Un **badge en coin** (ex : « 🎮 L1 ») indique la couche active.

### Carte des boutons

Appuie sur **Start** (ou le bouton « Afficher la carte des boutons » dans Paramètres) pour afficher la liste de toutes les actions, groupée par couche — le lecteur, ses trois couches LB / RB / LB+RB, le browser et les sticks. Les durées d'avance et de recul y sont celles que tu as réglées, et les dossiers rapides y portent leurs vrais noms.

La liste se répartit en colonnes selon la largeur de l'écran : une seule sur téléphone, quatre sur un écran de bureau, six sur un affichage très large. **D-pad ↑/↓** fait défiler, **B** ou **Start** ferme.

### Fenêtres et manette

Toutes les fenêtres de Hoard (tags, renommage, nouveau dossier, sélecteur de dossier, file de téléchargements, écran de code PIN, écran de connexion) se pilotent à la manette : **D-pad** parcourt les champs et les boutons, **A** active celui qui est sélectionné, **B** ferme la fenêtre. Aucun écran ne demande de reprendre la souris.

### Paramètres manette

Dans **Paramètres → 🎮 Manette** :

| Paramètre | Description |
|-----------|-------------|
| **Manette activée** | Active / désactive complètement la détection gamepad |
| **Retour haptique** | Vibration courte sur play/pause, seek, vu/non vu (Chrome uniquement) |
| **Zone morte** | Seuil de détection des sticks (défaut 20%). Augmenter si les sticks dérivent. |

---

## Connexion

Quand Hoard est configuré avec un identifiant et un mot de passe (variables
`HOARD_AUTH_USER` / `HOARD_AUTH_PASS`, voir le guide d'installation), l'ouverture
affiche un **écran de connexion aux couleurs de Hoard** — plus la fenêtre grise du
navigateur, qui se pilotait mal à la manette sur le Steam Deck et le Steam Frame.

- **Une seule saisie.** La connexion est retenue **30 jours**, et le décompte
  repart dès que tu utilises Hoard : en usage régulier, tu ne ressaisis jamais
  rien. Chaque appareil a sa propre connexion.
- **À la manette** : le **D-pad** passe d'un champ à l'autre, **A** ouvre le
  clavier sur le champ sélectionné, puis **A** sur « Se connecter ».
- **Si la session expire** pendant que tu navigues, l'écran revient et tu
  reprends exactement où tu en étais — pas de page rechargée, pas de lecture
  perdue.
- **Tout déconnecter d'un coup** : définis la variable `HOARD_SECRET_KEY` et
  change sa valeur. Toutes les sessions, sur tous les appareils, cessent
  immédiatement d'être valables.

> **Le code PIN est autre chose.** Il verrouille l'écran d'une session déjà
> ouverte, sur ton propre appareil ; la connexion décide si le serveur te répond.
> Les deux restent indépendants.

> **`curl` continue de fonctionner** avec `-u identifiant:motdepasse`, comme
> avant — utile pour les scripts.

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

> **Le lien contient un jeton d'accès personnel.** La bookmarklet s'exécute sur la
> page web de quelqu'un d'autre : ton navigateur n'y envoie jamais tes identifiants
> Hoard, et c'est ce jeton qui lui permet d'atteindre Hoard. Il autorise deux
> choses et rien d'autre : lancer un téléchargement, et en suivre l'avancement. Il
> ne permet ni de parcourir, ni de déplacer, ni de supprimer tes fichiers. Ne
> partage pas ce lien. Si ça t'arrive par erreur, utilise **🔑 Nouveau jeton** dans
> les paramètres : l'ancien lien cesse aussitôt de fonctionner, et tu réinstalles
> le favori en glissant le nouveau lien.

### Télécharger une vidéo

**Depuis n'importe quelle page web** — clique sur la bookmarklet. Elle soumet le téléchargement **en arrière-plan** et injecte une fenêtre de statut en direct directement dans la page courante — aucune navigation, aucun onglet ouvert. Le dialogue progresse à travers ⌛ « Analyse de l'URL… » → 📥 « Téléchargement… X% » → ✅ « Terminé ! » (fermeture automatique après 4 s). Si la file est occupée, il affiche ⏳ « En attente dans la file… — titre.mp4 » jusqu'à ce qu'un slot se libère. Tu peux annuler le job depuis le dialogue ou depuis le modal de file de téléchargement de Hoard.

> **Sites avec une CSP restrictive** : certains sites (souvent des sites de streaming chargés de publicités) bloquent, via leur `Content-Security-Policy`, les requêtes sortantes vers un domaine tiers comme celui de Hoard. Dans ce cas, la bookmarklet affiche ℹ️ « Hoard injoignable depuis cette page » et ouvre automatiquement Hoard dans un nouvel onglet pour y terminer le téléchargement.

> **« Hoard : accès refusé »** : le favori a été enregistré avant que le jeton ne
> soit régénéré. Ouvre les paramètres et glisse à nouveau le lien pour le remplacer.

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

### Historique des téléchargements

Le modal **📥** comporte deux parties :

- **En cours** — la file du moment (progression, annulation, retrait), qui disparaît une fois vidée.
- **Historique** — la liste **permanente** de tout ce qui a été téléchargé, conservée en base de données. Contrairement à la file, elle survit au redémarrage du NAS et n'expire pas.

Chaque ligne indique le nom du fichier, la date et le résultat :

| Statut | Signification |
|--------|---------------|
| ✓ Terminé | Le fichier est arrivé. Le bouton **Aller au fichier** ouvre son dossier et le met en évidence. |
| ✗ Échec | Le téléchargement a raté. Le message d'erreur est affiché sous la ligne. |
| ⊘ Annulé | Tu as arrêté le téléchargement. |
| ⚠ Interrompu (redémarrage) | Hoard s'est arrêté pendant le téléchargement. Le fichier n'est pas arrivé — il faut le relancer. |

Le bouton **Vider** efface l'historique (les fichiers déjà téléchargés ne sont pas touchés) ; **✕** retire une seule ligne.

Par défaut l'historique est conservé **sans limite** — c'est justement ce qui permet de retrouver un ajout ancien. Pour le borner : **Paramètres → Maintenance → Historique des téléchargements**, en nombre de jours (`0` = sans limite).

### Relancer un téléchargement

Chaque ligne de l'historique porte un bouton **↻**. Il remet la même vidéo en file d'attente, sans avoir à retrouver la page d'origine.

C'est utile pour les entrées **✗ Échec**, **⊘ Annulé** et **⚠ Interrompu** : le fichier n'est pas là, mais son adresse est conservée.

- Sur une entrée qui avait **réussi**, Hoard demande confirmation : la relance produit un **second** fichier à côté du premier, nommé `… (2)`.
- Hoard conserve la page d'origine du téléchargement et la retransmet, sans quoi beaucoup d'hébergeurs vidéo refuseraient la relance.
- En revanche, **les cookies de la session ne sont pas conservés** — ce sont des identifiants. Pour un site qui demande une connexion, c'est le fichier `cookies.txt` indiqué dans les réglages qui prend le relais.

### Où atterrissent les fichiers

Le modal 📥 affiche la destination sous deux formes : le nom relatif (ex. `Downloads`) et le **chemin complet** (ex. `/media/Downloads`). Si le dossier n'existe pas encore, la mention « sera créé » l'indique.

C'est important parce que le dossier de destination est **créé automatiquement** : une valeur de travers dans les réglages ne provoque aucune erreur, elle crée simplement un dossier ailleurs, où tous les téléchargements s'accumulent sans que rien ne le signale.

### Deux vidéos, deux fichiers

Quand la bookmarklet envoie le titre de la page comme nom de fichier, deux vidéos différentes d'un même site portent souvent le **même** titre. Hoard ajoute alors un suffixe — `Ma video.mp4`, puis `Ma video (2).mp4` — exactement comme un navigateur.

Sans cela, l'outil de téléchargement voyait un fichier du même nom, **sautait le téléchargement sans rien dire**, et la vidéo était perdue alors que l'interface affichait « Terminé ». Si le cas se présente malgré tout (téléchargement lancé sans nom de fichier), l'entrée passe désormais en **échec** avec un message qui explique quoi faire, jamais en « Terminé ».

### Paramètres

| Paramètre | Description |
|-----------|-------------|
| **Durées de seek** | Quatre niveaux configurables dans **Paramètres → Player** : court (défaut 10 s), moyen (30 s), long (60 s), très long (120 s). Utilisés par les boutons, les raccourcis clavier et les double-taps. |
| **Activer le transcodage** | Quand désactivé, Hoard envoie toujours le fichier original (`/api/file`) sans appeler le transcodeur. Utile si votre NAS est lent ou si votre navigateur lit nativement le format. |
| **Initial sweep par défaut** | Démarre les vidéos neuves à N secondes au lieu de 0. S'applique seulement si le fichier n'a aucune progression enregistrée. `0` le désactive globalement. |
| **Dossiers home** | Liste de dossiers nommés affichés sur l'écran d'accueil. Ajouter/supprimer dans **Paramètres → Dossiers home**. |
| **Dossier de téléchargement** | Dossier cible, relatif à la racine média (défaut : `Downloads`). Le **chemin complet** est affiché sous le champ, et un avertissement apparaît si le dossier n'existe pas encore — il sera créé au premier téléchargement. Le bouton **📂 Parcourir…** permet de le choisir par navigation plutôt qu'en le tapant. |
| **Chemin du fichier cookies** | Chemin absolu vers un fichier `cookies.txt` au format Netscape. Utile pour les sites qui nécessitent une authentification. |
| **Historique des téléchargements** | Nombre de jours conservés dans l'historique (**Paramètres → Maintenance**). `0` = sans limite (défaut). |

### À propos des cookies

La bookmarklet transmet le `document.cookie` de la page source. Attention : les **cookies HttpOnly ne sont pas accessibles en JavaScript** — pour les sites qui en ont besoin (ex : plateformes de streaming), exporte un fichier `cookies.txt` avec une extension navigateur et renseigne son chemin dans les paramètres.

---

## Maintenance

Section **Paramètres → Maintenance**, pour les opérations d'exploitation courantes.

### Journal

Hoard enregistre ses événements (téléchargements lancés, terminés, échoués, demandes de redémarrage) dans un fichier conservé **30 jours**, en plus des logs du conteneur. Le journal est consultable directement ici :

- Choix du nombre de lignes affichées (100 / 500 / 2000).
- Filtre par niveau : tous, info, avertissements, erreurs.
- **↻** actualise, **Copier** met le contenu dans le presse-papier (pratique pour le coller dans un ticket).

Les lignes sont en ordre chronologique, les plus récentes en bas.

### Redémarrer Hoard

Le bouton **↻ Redémarrer Hoard** relance l'application sans passer par Portainer ni le NAS. Utile quand un réglage bas niveau a changé, ou en cas de comportement anormal.

- Si un téléchargement est en cours, Hoard demande une confirmation supplémentaire : le redémarrage **interrompt définitivement** le téléchargement (il apparaîtra comme *Interrompu* dans l'historique).
- Une fois lancé, la page attend le retour du serveur et se recharge toute seule (jusqu'à 60 s). Au-delà, un message invite à vérifier le conteneur.
- Hoard ne se relance pas lui-même : c'est le conteneur qui le fait (`restart: unless-stopped` dans `docker-compose.yml`). En dehors d'un conteneur, le bouton **arrête** l'application — le message de confirmation le dit explicitement.

---

## Disposition responsive

| Écran | Mode |
|-------|------|
| Largeur > 700 px | Vue divisée : liste à gauche, player à droite |
| Largeur ≤ 700 px | Liste plein écran, player en overlay |

## Installer comme une app

Sur les navigateurs qui prennent en charge l'installation des web apps, Hoard peut maintenant s'installer comme une application autonome au lieu de rester dans un onglet classique. Sur iPad et iPhone, utilise l'action **Ajouter à l'écran d'accueil** du navigateur pour obtenir le même lancement en mode standalone.

Cette couche d'installation ne met en cache que le shell de l'application pour rouvrir l'interface plus vite. Hoard a toujours besoin d'une connexion active au NAS pour les appels API, la navigation dans les dossiers et la lecture vidéo.
