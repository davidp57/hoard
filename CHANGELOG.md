# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Plein écran fenêtré par défaut sur PC (BL-066)** : sur desktop, `F` et le bouton plein écran passent désormais en mode **immersif dans la fenêtre** (vidéo plein cadre + UI masquée, sans quitter le navigateur) ; `Maj+F` déclenche le vrai plein écran de l'OS. Sur tablette/tactile (iPad), le comportement est inchangé (vrai plein écran). Toutes les actions « spéciales plein écran » (lecture auto du suivant, dialogues supprimer/déplacer, etc.) fonctionnent à l'identique en mode fenêtré.
- **Clavier — Échap remonte d'un cran (BL-068)** : sur PC, quand aucun média n'est ouvert, `Échap` remonte d'un niveau dans l'arborescence (comme le bouton B au pad), via une fonction `navigateUp()` partagée. La cascade existante (fermer dialogue → quitter plein écran → fermer le player) est conservée et prioritaire. Les flèches ←/→ n'ont plus d'effet en mode navigation (alignement sur le D-pad).

### Removed
- **Endpoint `/api/stream` (BL-067)** : suppression de l'endpoint de streaming hérité, devenu code mort depuis la migration vers `/api/file` (BL-053). La lecture de tout média passe par `/api/file` (validation Range/416 incluse). Docs mises à jour.

### Fixed
- **Lisibilité de l'aide clavier (BL-065)** : la fenêtre d'aide (`?`) était illisible sur PC/Firefox (texte sombre sur fond sombre car le `<dialog>` héritait de la couleur de texte par défaut du navigateur). Couleur de texte désormais explicite.
- **Délai et feedback réseau (BL-037)** : les appels critiques (listing, recherche, sauvegarde de progression, déplacement, suppression) passent par un wrapper `apiFetch` avec timeout (15 s) et affichent un toast en cas de lenteur/erreur réseau, au lieu de rester silencieusement bloqués (utile au réveil du NAS).
- **Atomicité des opérations fichiers (BL-034)** : la suppression et le déplacement mettent désormais à jour la base **avant** l'opération disque, avec rollback si celle-ci échoue. Plus de lignes de progression/segments orphelines (ou mal réécrites) lorsqu'une suppression/déplacement échoue.
- **Fuite mémoire des jobs terminés (BL-033)** : les jobs de téléchargement/export en état terminal (`done`/`error`/`cancelled`) sont désormais purgés du store en mémoire après un TTL (par défaut 1 h, configurable via `JOB_TTL_SECONDS`). Évite la croissance illimitée de la mémoire sur un serveur de longue durée.
- **Audio silencieux pour certaines vidéos** : les fichiers avec audio AC3, EAC3 (Dolby Digital/Plus), DTS ou TrueHD étaient lus sans son car le navigateur ne supporte pas ces codecs nativement. Hoard détecte maintenant ces codecs et route automatiquement vers le transcodage (si activé) ; si le transcodage est désactivé, un avertissement est affiché.

### Added
- **Sous-titres sidecar (BL-008)** : les fichiers `.srt` / `.ass` situés à côté de la vidéo (même radical) sont détectés et proposés comme pistes de sous-titres. Conversion à la volée en WebVTT côté serveur (le `.ass` est rendu en texte simple, sans style). Bouton 💬, touche `C` et action manette (L1+A) pour cycler entre les pistes / désactivé.
- **Renommage de fichiers et dossiers (BL-006)** : nouveau bouton ✏ dans la liste et raccourci clavier `R` ouvrant une fenêtre de renommage. Endpoint `POST /api/files/rename` avec validation du nom (pas de séparateur), détection de collision (409) et atomicité DB-first ; le renommage d'un dossier migre aussi la progression/segments de tous les fichiers qu'il contient.
- **Tri par taille et par état de lecture (BL-002)** : la barre de tri propose désormais, en plus de Date et Nom, un tri par **Taille** et par **État** (non vu / en cours / vu). Le sens (asc/desc) reste configurable, et le tri par défaut est paramétrable dans les réglages.
- **Aide à la découverte des gestes tactiles (BL-038)** : au premier lancement du player sur un appareil tactile, un overlay présente les principaux gestes (double-tap reculer/avancer, tap pause, glissés bord pour volume/luminosité). Affiché une seule fois (flag `gestures_overlay_seen` persisté), uniquement sur écrans tactiles (`pointer: coarse`).
- **Transcodage audio uniquement** : nouveau paramètre "Transcodage audio uniquement" qui copie le flux vidéo tel quel (sans réencodage) et ne réencode que l'audio en AAC. Beaucoup plus léger sur le CPU du NAS. Idéal pour les fichiers MKV/HEVC+EAC3 sur Chrome/Edge (qui supportent HEVC nativement). Si le codec vidéo n'est pas supporté par le navigateur, un message d'erreur explicite est affiché.

### Security
- **Authentification HTTP Basic optionnelle (BL-011)** : définir `HOARD_AUTH_USER` et `HOARD_AUTH_PASS` impose une authentification Basic sur toutes les requêtes. Désactivée par défaut (comportement inchangé). Pensée pour l'exposition hors LAN derrière un reverse proxy / HTTPS, sans système de comptes.
- **Hachage du PIN avec scrypt (BL-030)** : le PIN est désormais haché avec `scrypt` (sel aléatoire par PIN, format `scrypt$sel$clé`) au lieu d'un SHA-256 sans sel. Les anciens PIN SHA-256 sont migrés de façon transparente lors de la première connexion réussie (aucune re-saisie requise).
- **Journal d'audit des opérations (BL-036)** : journalisation `INFO` des suppressions, déplacements, démarrages/fins/échecs de téléchargement et modifications de réglages (avec l'IP cliente), et `WARNING` sur échec de vérification du PIN. Niveau pilotable via `LOG_LEVEL`.
- **Thread-safety de `MEDIA_ROOT` (BL-032)** : les accès au `MEDIA_ROOT` global (modifiable via `POST /api/settings`) passent par un verrou et `get_media_root()`. `safe_path()` capture la racine une seule fois par appel, éliminant une lecture incohérente possible pendant une mise à jour concurrente (risque de contournement du contrôle de chemin).
- **En-têtes de sécurité HTTP (BL-029)** : un middleware ajoute `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer` et une `Content-Security-Policy` sur toutes les réponses. La CSP préserve le frontend inline, l'import Google Fonts et les lecteurs média/PDF.js (`blob:`/`data:`).
- **Validation du chemin de cookies de téléchargement (BL-031)** : le réglage `download_cookies_path` est désormais validé à l'enregistrement (`POST /api/settings`) — le chemin doit être absolu, porter l'extension `.txt`, exister et être lisible, sinon une erreur HTTP 422 explicite est renvoyée. Empêche de pointer yt-dlp vers un fichier arbitraire.

### Accessibility
- **Accessibilité (BL-039)** : `aria-label` (en français) ajoutés sur les boutons icône principaux (accueil, paramètres, file de téléchargement, lecture/pause, seek, plein écran, muet), indicateur de focus clavier (`:focus-visible`), et contraste de `--text-dim` relevé (#666 → #8a8a8a) pour respecter le seuil WCAG AA sur fond sombre.

### Performance
- **Index couvrant sur `progress` (BL-035)** : ajout de `idx_progress_active (duration, position, path)`. La construction de la carte de progression dans `/api/files` et `/api/search` (`WHERE duration > 0`) s'exécute désormais en balayage *index-only*, sans lecture de lignes, sur les bibliothèques volumineuses. (`progress.path` étant déjà clé primaire, un index sur `path` aurait été redondant.)

---

## [v2.2.0] - 2026-05-20

### Added
- **Harmonisation commandes clavier / pad / touch (Lot 11)** :
  - **Esc enrichi** : 1er Esc quitte le plein écran vidéo ; 2e Esc ferme le player (équivalent au Y puis B de la manette).
  - **↑/↓ contextuel** : quand le player est inactif, les flèches ↑/↓ déplacent le curseur dans la liste de fichiers (réutilise le curseur gamepad). Quand le player est actif, comportement volume inchangé.
  - **Entrée** : valide l'élément sous le curseur liste (quand aucun média en cours).
  - **W** : bascule l'état vu / non vu du fichier en cours (équivalent au bouton X de la manette).
  - **[ / ]** : diminue / augmente la vitesse de lecture (0,5× → 1× → 1,5× → 2×, style VLC).
  - **Manette L3** (clic stick gauche) : mute / son.
  - **Manette R3** (clic stick droit) : cycle vitesse de lecture.
  - **Aide clavier (`?`)** : tableau réorganisé par sections (Navigation, Lecture, Volume & Vitesse, Player, Fichiers) avec toutes les nouvelles commandes.
- **Navigation clavier dans les dialogues** : dans les dialogues (suppression, déplacement, export), les flèches ↑/↓ naviguent entre les options, Entrée valide et Échap annule — sans la souris.
- **Aide raccourcis clavier (`?`)** : la touche `?` ouvre/ferme un panneau listant tous les raccourcis clavier et la navigation dans les dialogues.
- **Diagramme manette Xbox dans l'overlay gamepad** : l'overlay manette affiche un SVG de la manette Xbox avec les actions annotées par des lignes de callout. Maintenir **LB** ou **RB** sur la manette physique fait s'afficher le bouton enfoncé (couleur or) et met à jour les callouts en temps réel pour montrer les actions de la couche correspondante (L1, R1 ou L1+R1). Deux onglets contexte permettent de basculer entre la vue Joueur et Browser.
- **Visionneuse d'images (BL-054)** : les images (JPG, PNG, GIF, WEBP, BMP, TIFF, AVIF) s'ouvrent dans un viewer intégré au panneau player. Navigation précédent/suivant (touches ← / →, boutons), bascule mode « plein écran » / « largeur ajustée ». La progression (index/total) est sauvegardée en base.
- **Lecteur d'archives BD/manga (BL-055)** : les fichiers `.cbz`, `.zip` et `.cbr` s'ouvrent comme des visionneuses page à page. La liste des images est extraite côté serveur (`/api/archive/list`) ; chaque page est servie à la demande (`/api/archive/image?index=N`). CBR nécessite `rarfile` + `unrar-free`.
- **Lecteur PDF (BL-056)** : les fichiers `.pdf` sont rendus via PDF.js v4 (ES module, inclus dans `frontend/pdfjs/`). Navigation page par page (← / →), zoom (+/−), mode ajustement largeur / taille originale. La page courante est sauvegardée en base.
- **Lecteur audio (BL-057)** : les fichiers audio (MP3, FLAC, OGG, M4A, AAC, WAV, OPUS) s'ouvrent dans un player audio minimaliste réutilisant l'élément `<video>` HTML5. Barre de progression cliquable, contrôles lecture/pause et seek ±10s, bouton fermer.
- **Champ `media_type` dans `/api/files` et `/api/search` (BL-053)** : chaque entrée fichier expose désormais `media_type` (`video`, `image`, `audio`, `pdf`, `archive`, `other`). Le progrès est retourné pour tous les types de médias (pas seulement les vidéos).
- **Endpoint `/api/file` (BL-053)** : remplace `/api/stream` pour servir tout type de fichier média avec support Range. `/api/stream` est conservé pour compatibilité.
- **Endpoints `/api/archive/list` et `/api/archive/image` (BL-055)** : liste les images d'une archive et extrait une image à un index donné.
- **Dépendance `rarfile>=4.0`** ajoutée à `backend/requirements.txt` ; `unrar-free` ajouté à l'image Docker.
- **D-pad auto-repeat** : maintenir une direction du D-pad dans le navigateur de fichiers (sans L1/R1, hors lecteur) déclenche la répétition automatique pour un défilement rapide (délai initial 400 ms, répétition 100 ms).
- **Bouton Rafraîchir (↻)** : bouton de rafraîchissement manuel dans la barre de tri. Vide le cache du dossier courant et recharge la liste.

### Changed
- **Suppression du rafraîchissement automatique** : le `setInterval` de 30 s est retiré. Les opérations de modification du filesystem (suppression, déplacement, création de dossier, découpe) continuent de rafraîchir la liste automatiquement.

### Fixed
- **Transcodage forcé malgré l'option désactivée (BL-064)** : le handler d'erreur vidéo (`video.onerror`) basculait inconditionnellement vers `/api/transcode` sans vérifier le paramètre « Transcodage activé ». L'option désactivée est désormais respectée : un toast informatif s'affiche à la place.
- **Dialogues invisibles en faux-fullscreen (manette)** : les dialogues d'action (suppression, déplacement, export…) avaient `z-index:100`, inférieur au conteneur `faux-fullscreen` (`z-index:200`). Ils sont désormais à `z-index:300` et restent visibles au-dessus de la vidéo. Corrige le bug où la 2e suppression consécutive via manette (LB+RB+B) ne montrait aucun dialogue.
- **Aide manette (overlay Start) : image agrandie dynamiquement** : le panneau d'aide manette passe de 620 px fixe à 75 vw (dynamique), rendant le diagramme du pad beaucoup plus lisible.
- **Curseur manette disparu après rafraîchissement** : `navigate()` sur le même chemin ne réinitialise plus `_gpCursorIdx` — le curseur est conservé sur place. `renderFiles()` maintient aussi le curseur lors des re-renders in-place (filtre, tri).

---

## [v2.1.0] - 2026-05-15

### Added
- **Indicateur de volume (OSD)** : une barre de volume s'affiche en bas à droite du player quand le volume est modifié (touches ↑/↓, manette D-pad, swipe vertical tactile). Elle indique l'icône 🔇/🔉/🔊, un niveau visuel et le pourcentage, puis disparaît automatiquement après 2,5 secondes. Remplace les toasts éphémères volume gamepad et swipe tactile.
- **Indicateur de progression en plein écran** : le mini-affichage de position (coin haut droit) remplace le texte `XX / YY` par : temps restant en plus grand, barre de progression globale (fine), et une barre zoomée (×2) qui matérialise le segment de 10 % courant au bon emplacement de la barre globale.
- **Lecture automatique du fichier suivant en plein écran** : après une suppression, un déplacement ou un découpage du fichier en cours de lecture en mode plein écran, le fichier suivant dans la liste est chargé et lancé automatiquement, et le mode plein écran est réactivé.
- **Taille de la fenêtre de zoom configurable** : le pourcentage de la barre de progression zoomée en plein écran est maintenant configurable dans les Paramètres (section 🎬 Player, « Zoom barre plein écran »). Valeur par défaut 20 %, plage 5–50 %. La barre zoomée est également agrandie visuellement (14 px au lieu de 8 px).
- **Multi-segments — socle backend (BL-047 + BL-048)** : nouvelle table `segments(id, path, seg_in, seg_out)` en SQLite. Endpoints `GET/POST /api/segments` et `DELETE /api/segments/{id}` pour gérer les segments par fichier. Endpoint `POST /api/files/export-segments` : exporte N segments en mode `individual` (un fichier par segment, via FFmpeg `-c copy`) ou `merged` (concat FFmpeg lossless via le concat demuxer). Par défaut, déplace le fichier original ET les fichiers exportés vers le dossier destination. Option `keep_original` pour conserver l'original en place. Segments effacés de la base après export réussi.
- **Multi-segments — frontend (BL-049 + BL-050 + BL-051)** : remplacement complet du système de découpe IN/OUT par le nouveau système multi-segments. La seekbar affiche des bandes colorées pour chaque segment validé et une zone hachurée pour le IN en attente. Une liste de chips sous la seekbar indique les segments (heure IN → OUT, couleur, bouton ×). Touche `I` = marquer le point IN (en attente), touche `O` = valider le segment OUT. Un bouton `✂ N` s'affiche dans les contrôles quand des segments existent. La modal d'export (touche `E`) propose le mode fusionné ou individuel, le dossier destination (dossiers rapides + saisie libre), et l'option conserver l'original. Manette : `L1+Y` = IN, `R1+Y` = OUT, `L1+R1+Y` = ouvrir la modal export, navigation interne au dialogue. Ancien système `cut_in`/`cut_out` entièrement supprimé du frontend.

### Fixed
- **Volume — curseur non mis à jour via gamepad/swipe** : `setVolume()` ne synchronisait pas le slider `#volume-slider` ; seul le clavier le faisait manuellement. Le slider est maintenant mis à jour dans `setVolume()` pour tous les modes de déclenchement.
- **Gamepad — plein écran impossible avec Y sous Firefox (PC)** : `requestFullscreen()` requiert un user gesture direct ; le polling gamepad via `requestAnimationFrame` n'en est pas un dans Firefox, provoquant un `NotAllowedError` silencieux. Quand `NotAllowedError` est levé, la fonction bascule désormais automatiquement sur le faux-fullscreen CSS, rendant le bouton Y symétrique (entrée et sortie) sur tous les navigateurs.
- **Gamepad — dialogues en plein écran (BL-046)** : les dialogues de suppression et de déplacement (`#delete-dialog`, `#move-dialog`) ne répondaient pas aux boutons gamepad en mode plein écran natif sur SteamDeck/Edge. Ils sont désormais convertis en `<div>` overlay (`position:fixed`, `z-index:100`) et déplacés dans `document.fullscreenElement` lors du `fullscreenchange`, identiquement à l'overlay d'aide gamepad. La détection dans `_gpDispatch` utilise une nouvelle fonction `_gpOpenModal()` qui inspecte les deux types de modals (div + `<dialog>`).
- **Gamepad — vidéo fantôme en arrière-plan (BL-044)** : après avoir confirmé une action (suppression, déplacement, découpe), une pression rapide sur A pouvait déclencher la lecture d'une vidéo en fond sonore. Résolu en réinitialisant immédiatement `_gpCursorIdx = -1` lors du dispatch de l'action de confirmation, avant que `navigate()` ne termine.
- **Gamepad — curseur perdu après action fichier (BL-043)** : supprimer, déplacer ou découper un fichier remettait le curseur de navigation au début de la liste. `_gpPendingRestoreIdx` sauvegarde la position avant l'action ; `renderFiles()` la restaure après le rechargement de la liste (clamped au nouvel index maximal). La restauration est désormais basée sur le chemin du fichier supprimé/déplacé (et non plus sur `_gpCursorIdx`), ce qui la rend fiable quel que soit le mode de déclenchement (gamepad, clavier, clic).
- **Gamepad — curseur à -1 après auto-play post-suppression (BL-052)** : après suppression d'un fichier en plein écran, le fichier suivant démarrait correctement via `_autoPlayNextFullscreen`, mais `playVideo` appelait ensuite `renderFiles()` sans `_gpPendingRestoreIdx` défini, réinitialisant `_gpCursorIdx = -1`. Résultat : commandes buggées, vidéo fantôme possible (régression BL-044), curseur à -1 à la sortie du plein écran. Corrigé en sauvegardant la position de la vidéo en cours dans `_gpPendingRestoreIdx` avant le `renderFiles()` final de `playVideo`.

### Changed
- **Gamepad — move dialog : confirmation en 2 étapes (BL-045)** : le dialogue de déplacement affiche maintenant un bouton « ↗ Déplacer » (désactivé jusqu'à sélection d'un dossier). Les boutons de dossier rapide *sélectionnent* la destination (sans déplacer immédiatement) ; D↑/D↓ navigue dans la liste, A valide le dossier sélectionné et bascule vers le bouton de confirmation, A confirme le déplacement, B annule à tout moment. Identique au flux du dialogue de découpe (`cut-dialog`).
- **Racine de navigation par défaut (BL-040)** : chaque home root peut être désignée comme racine par défaut (colonne `is_default` en base, endpoint `POST /api/home-roots/{id}/set-default`). L'app navigue directement vers la racine par défaut au démarrage et après validation du PIN, sans passer par l'écran de sélection. Un indicateur visuel (🏠, bordure accent, badge « défaut ») et un bouton « ⌂ » permettent de changer la racine par défaut depuis les Paramètres.
- **Contrôles manette étendus** :
  - `L1+R1+B` → supprimer le fichier courant (lecteur ou curseur browser)
  - `L1+R1+X` → déplacer le fichier courant (lecteur ou curseur browser)
  - Navigation dans les **Paramètres** : D↑/D↓ pour défiler, B ou Start pour fermer
  - Navigation dans les **dialogues** : A = confirmer (supprimer), B = annuler ; dans le dialogue de déplacement, D↑/D↓ sélectionne le dossier, A valide
  - Mise à jour de l'overlay d'aide (`Start`) avec les nouveaux raccourcis contextuel (browser, paramètres, dialogues)

### Fixed
- **Overlay manette (Start)** : converti en `<dialog>` avec `showModal()` — désormais visible en plein écran natif et hors plein écran. L'ancienne div `position:fixed` était masquée par le mode fullscreen du navigateur.
- **Rafraîchissement auto** : la liste ne se rafraîchit plus quand un fichier vidéo est chargé (même en pause). La condition `video.paused` est remplacée par `!currentFile` pour éviter d'interrompre une session de lecture.
- **Dockerfile** : correction des fins de ligne CRLF sur `entrypoint.sh` lors du build depuis Windows (`sed -i 's/\r//'`).

### Changed
- **UX « Ajouter une racine »** : le bouton n'utilise plus `currentPath` silencieusement. Il ouvre désormais la modale de navigation pour choisir le dossier, puis demande un nom (pré-rempli avec le nom du dossier sélectionné).
- **Bouton « ⌂ Dossier de départ »** dans les Paramètres : quand des home roots existent, il ouvre le sélecteur de dossier pour *ajouter* une nouvelle racine (au lieu de modifier `MEDIA_ROOT` directement). Le comportement historique (changer `MEDIA_ROOT`) est conservé si aucune home root n'est configurée.
- **`navigateHome` (bouton 🏠)** : navigue vers la racine par défaut si l'utilisateur n'y est pas déjà ; appuyer une seconde fois depuis la racine par défaut affiche l'écran de sélection multi-racines.
- **Tags de fichiers** : les tags sont stockés en base SQLite (`file_tags`), affichés comme badges dans la liste, et un filtre par tag apparaît dynamiquement dans la barre de tri.
- **Sélecteur de destination libre (BL-005)** : bouton « 📂 Parcourir… » dans la fenêtre de déplacement permettant de choisir n'importe quel dossier de l'arborescence comme destination.
- **Recherche dans les noms de fichiers (BL-012)** : champ de recherche dans la barre de tri ; la recherche est récursive dans le dossier courant via le nouvel endpoint `GET /api/search`.
- **Métadonnées vidéo dans l'UI (BL-016)** : codec, résolution, durée et bitrate affichés sous le titre du fichier en cours de lecture via `GET /api/media-info`.
- **Vitesse de lecture (BL-010)** : bouton de cycle de vitesse (0.5×, 1×, 1.5×, 2×) dans les contrôles du player ; la vitesse est réinitialisée à chaque ouverture de fichier.
- **Rafraîchissement automatique de la liste (BL-009)** : la liste se met à jour toutes les 30 secondes quand le navigateur est actif, l'onglet visible et la vidéo en pause.
- **Dossiers home multiples (BL-023)** : support de plusieurs racines de navigation avec gestion complète en base (`home_roots`) et interface de sélection.
- **Support manette / gamepad (BL-024)** : intégration de la Gamepad API avec boucle `requestAnimationFrame`, système 4 couches (base / L1 / R1 / L1+R1), contrôles complets du lecteur (lecture, seek, volume, plein écran, vu/non vu, déplacement rapide), navigation dans le navigateur de fichiers au gamepad, scrubbing analogique stick gauche, volume analogique stick droit, badge HUD de couche active, overlay aide (Start button), toasts de connexion/déconnexion, retour haptique Chrome, et section « 🎮 Manette » dans les Paramètres (activation, deadzone, haptique). Paramètres `gamepad_enabled`, `gamepad_deadzone`, `gamepad_haptic`, `gamepad_mapping` ajoutés au backend SQLite.

- **Sweep initial configurable (BL-017)** : nouveau paramètre global `initial_sweep_seconds` + surcharge par dossier. Les vidéos jamais ouvertes démarrent à l'offset configuré (ex. 10 minutes) ; les vidéos avec progression sauvegardée reprennent normalement à leur position mémorisée.
- **Endpoint métadonnées lecture (BL-019)** : ajout de `/api/media-info` basé sur `ffprobe` pour inspecter le conteneur, les codecs, le bitrate, la fréquence d'images et les propriétés audio avant de décider du mode de lecture.
- **Shell PWA optionnel (BL-014)** : Hoard embarque désormais un manifeste web app, un service worker minimal et des ajustements standalone pour permettre l'installation comme application sur les navigateurs compatibles (iPad, laptop Windows), sans modifier le modèle de lecture en ligne depuis le NAS.
- **4 niveaux de seek unifiés (BL-021)**: les raccourcis clavier, le double-tap et les boutons skip utilisent désormais 4 durées configurables (`seek_short`, `seek_medium`, `seek_long`, `seek_xlong`) au lieu des anciennes valeurs `doubletap_*` séparées.
- **Nouveaux raccourcis clavier (BL-021)**: navigation vidéo suivante/précédente (PageDown/PageUp), muet (M), cycle aspect ratio (A), marquer points IN/OUT (I/O), ouvrir découpe (C), ouvrir déplacement (D), supprimer (Suppr), sauvegarder position initiale (S), aide raccourcis (?).
- **Icône aspect ratio distincte (BL-025)**: le bouton Fit/Fill affiche désormais une icône SVG de cadre au lieu du symbole ⛶ qui ressemblait au bouton plein écran.
- **Toast systématique sur tous les seeks (BL-026)**: chaque seek (bouton, clavier, swipe) affiche un toast de confirmation indiquant le delta réel.
- **Modaux fullscreen compatibles (BL-021)**: les fenêtres Déplacer, Découper, Supprimer et l'aide clavier utilisent désormais les `<dialog>` HTML natifs qui restent visibles au-dessus du plein écran natif (plus de blocage par `window.confirm()`).
- **Zone de reveal des contrôles en fullscreen restreinte (BL-026)**: le déplacement de la souris ne révèle les contrôles qu'en bas de l'écran (10 %), évitant l'affichage intempestif pendant la lecture.
- **Option pour désactiver le transcodage (BL-022)**: nouveau paramètre `transcode_enabled` (défaut : activé). Quand il est désactivé, le player utilise toujours `/api/stream` sans appeler `/api/transcode`, ce qui réduit la charge CPU du NAS pour les formats supportés nativement.

### Fixed
- **Sonde lecture — pas de transcodage prématuré (BL-019)** : les formats comme HEVC-in-MP4 conservent désormais le chemin natif `/api/stream` même quand `canPlayType()` ou `MediaCapabilities` restent conservateurs. Le repli vers `/api/transcode` n'est déclenché que sur les formats explicitement marqués `fallback` ou lors d'un vrai échec de lecture.
- **Contrôles plein écran — zone de déclenchement restreinte (BL-018)** : afficher/masquer les contrôles est à nouveau limité à la zone basse centrale près des boutons, et non à l'ensemble du conteneur plein écran.
- **Tap simple sur les zones latérales — plus d'action centrale (BL-018)** : les zones de seek gauche et droite en plein écran ignorent désormais les taps simples et ne déclenchent plus le basculement lecture/pause ni les contrôles.
- **Plein écran natif sur les postes tactiles (BL-020)** : la branche `navigator.maxTouchPoints > 0` a été supprimée de `toggleFullscreen()`. Les appareils comme le SteamDeck (tactile + `requestFullscreen()` supporté) utilisent désormais le vrai plein écran natif. iPad/Safari continue d'utiliser le faux-fullscreen CSS car `document.fullscreenEnabled` y est déjà `false`.

### Changed
- **Masquage automatique des contrôles plein écran (BL-018)** : à l'entrée en plein écran, les contrôles se masquent automatiquement. Sur desktop ils réapparaissent sur mouvement souris ou interaction clavier ; sur écran tactile via le geste basse-centrale existant.
- **Sélection intelligente du mode de lecture (BL-019)** : le player sonde le support natif via `canPlayType()` et `MediaCapabilities` quand les métadonnées sont disponibles, et ne bascule vers `/api/transcode` que si le support n'est pas confirmé ou en cas d'échec réel.
- **Interface sweep initial simplifiée (BL-017)** : le player utilise désormais une action compacte unique pour enregistrer la position actuelle comme point de départ par défaut du dossier, à la place d'un éditeur inline permanent.

## [2.0.0] - 2026-04-06

### Added
- Video download via yt-dlp: bookmarklet + 📥 button in the header let you send any web video to Hoard for download on the NAS
- `POST /api/download` endpoint: accepts a URL and optional `cookies`, `referer`, and `title` fields; creates a background job, returns a `job_id`
- **Download queue widget**: 📥 header button now shows a badge with the count of active downloads and opens a unified modal combining the add-form and a live queue list
- **Download queue modal**: lists all running/completed/failed downloads with individual progress bars; completed or failed entries can be dismissed with ✕
- **Download persistence across page reloads**: on page init the frontend reconnects to any jobs still running in the backend (downloads never stop when you close the tab)
- `DELETE /api/jobs/{job_id}` endpoint to remove a job from the in-memory store
- **Filename hint**: bookmarklet now captures `document.title` and pre-fills a "Nom du fichier" field in the modal; the value overrides yt-dlp's automatic title, giving clean filenames for embed pages
- `_sanitize_filename()` helper: strips characters invalid in filenames on Windows/Linux, caps at 180 chars
- **Server-side HTML video sniffing**: when yt-dlp reports "Unsupported URL", the backend fetches the page HTML and scans for `<video>`, `<source>`, `<iframe>`, `<meta property="og:video*">`, inline `<script>` blocks, and `data-*` attributes pointing to known video-hosting domains (BunnyCDN, YouTube embed, Vimeo, JW Platform, Brightcove, Kaltura) or direct media files (`.mp4`, `.m3u8`, `.webm`, `.mkv`) — covers JS-injected players whose URL never appears in the raw HTML. If a video source is found, yt-dlp is retried automatically.
- New settings: `download_folder` (target folder relative to `MEDIA_ROOT`, default `Downloads`) and `download_cookies_path` (path to a persistent Netscape cookies.txt file)
- Cookie passthrough: bookmarklet captures `document.cookie` and sends it with the request; a persistent cookies.txt file is also supported for authenticated sites
- Bookmarklet auto-generated in Settings → Downloads; drag-to-bookmark instructions provided
- SSRF protection on `/api/download`: `file://`, localhost, and RFC-1918 private network addresses are rejected
- **Smart video source detection**: bookmarklet captures `<video>.currentSrc` from the page DOM — 6 strategies including iframe detection for BunnyCDN / YouTube / Vimeo embeds
- Referer header passthrough: when downloading a direct video URL, the original page URL is sent as `Referer`

- **Native HTTPS support**: set `SSL_CERTFILE` and `SSL_KEYFILE` environment variables to serve Hoard over HTTPS without a reverse proxy. Commented instructions in `docker-compose.yml` show how to mount a cert folder and enable it. Generate a self-signed cert with `openssl req -x509 -newkey rsa:4096 ...` or a locally-trusted cert with `mkcert`.
- **Sequential download queue**: downloads are now processed one at a time — new jobs wait in a `pending` state until the current download finishes, preventing bandwidth overload.
- **Stop button on downloads**: each pending or running download now shows a ⏹ stop button in the queue modal; clicking it cancels the job immediately (pending) or aborts the active yt-dlp transfer (running). Partial `.part` files left by yt-dlp are deleted automatically on cancellation.
- **Auto-refresh download folder**: when a download completes, the file browser automatically refreshes if the user is currently browsing the download folder.
- **Two-phase download preparation**: when a job is submitted (via bookmarklet or UI), a dedicated thread immediately runs phase 1 — sets a filename preview from the page title and transitions the job `pending` → `resolving` → `pending` — before placing it in the queue. The bookmarklet toast now shows ⌛ "Analyse de l'URL…" right away, then ⏳ "En attente — titre.mp4" while waiting, instead of being stuck on the initial connection state.
- **Bookmarklet queue awareness**: the bookmarklet status dialog now correctly distinguishes ⏳ "En attente dans la file…" (queued, not yet started) from ⌛ "Analyse de l'URL…" (running), and shows ⏹ "Annulé" if the job is cancelled from the Hoard UI.

### Fixed
- Cloudflare anti-bot 403 errors: yt-dlp now impersonates Chrome via `curl-cffi` (`impersonate` option at top-level, `curl-cffi>=0.10.0,<0.15.0`)
- Invalid Netscape cookie file format: domain is now prefixed with `.` as required when `include_subdomains=TRUE`
- Bookmarklet/PIN flow: after entering the PIN the download queue modal no longer opened — two call sites of `openDownloadModal` had not been renamed to `openDlQueueModal`
- Bookmarklet: submits the download directly to Hoard in the background via `fetch()` — no page navigation, no modal — a status dialog injected into the current page shows live progress: "Connexion à Hoard…" → "Analyse de l'URL…" → "Téléchargement… X%" → "Terminé !" (auto-close) or "❌ error" (manual close). The `#download?` hash redirect is kept for backward compatibility.

## [1.0.0] - 2026-04-05

### Added
- Settings page with PIN lock (numeric, SHA-256 hashed), accessible via ⚙️ button in header
- Configurable touch gestures: enable/disable per category, edge zone %, swipe threshold, sensitivity, double-tap values
- Configurable privacy timeout (auto-close player after N minutes of inactivity)
- Configurable watched threshold (default 90%)
- Home folder and sort order are stored in backend DB (migrated from localStorage)
- Multi-tap seek accumulation: N taps = (N−1) × base seek value
- 3 vertical zones on both left and right seek edges (top=fastest, bottom=slowest)
- Fit/Fill toolbar button (replaces triple-tap gesture)
- Full bilingual documentation (EN + FR): user guide, installation, developer guide, getting-started guide
- Page Visibility API privacy: player auto-closes when device wakes after timeout
- Seek bar touch area extended (±20px) to prevent swipe conflict
- Double-tap right zone split into 3 vertical thirds (+30s / +60s / +90s base values)

### Changed
- Project renamed from MediaBrowser to Hoard
- Docker image: `ghcr.io/davidp57/nas-vid-bro` → `ghcr.io/davidp57/hoard`
- docker-compose service name: `mediabrowser` → `hoard`
- README rewritten as bilingual entry point

[Unreleased]: https://github.com/davidp57/hoard/compare/v2.2.0...HEAD
[v2.2.0]: https://github.com/davidp57/hoard/compare/v2.1.0...v2.2.0
[v2.1.0]: https://github.com/davidp57/hoard/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/davidp57/hoard/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/davidp57/hoard/releases/tag/v1.0.0
