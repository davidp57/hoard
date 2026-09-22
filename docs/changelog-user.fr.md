# Changelog utilisateur — Hoard 🐦

Journal des changements visibles par l'utilisateur, sans jargon technique.

---

## [Non publié]

### Ajouté

- **Tes sticks font la même chose en vidéo 180° et sur un écran normal.** Si tu
  as activé *inverser les sticks*, l'avance/recul fin quittait le stick droit dès
  que tu passais en VR et n'y revenait qu'en sortant. Maintenant, dès que tu
  relâches **R2**, les deux sticks reprennent exactement leurs rôles habituels —
  avance/recul, volume, et la vitesse au clic du stick droit. **R2** maintenu
  reste le seul moment où le stick droit sert à regarder autour.

- **Tu gardes la barre du lecteur et le temps sous les yeux en vidéo 180°.**
  Jusqu'ici, dès que le lecteur passait en côte à côte, la barre de progression,
  la bulle de volume et l'afficheur du temps disparaissaient — ils auraient été
  coupés en deux et illisibles. Avec l'écran entier en côte à côte ce n'est plus
  le cas : chaque œil reçoit une image complète, donc chacun reçoit aussi sa
  barre. Tu sais de nouveau où tu en es dans le fichier sans avoir à toucher à
  quoi que ce soit.

- **Toute l'interface s'affiche en côte à côte pour des lunettes XR.** Avec des
  lunettes en mode 3D, l'image est coupée en deux tout le temps, pas seulement
  pendant une vidéo : l'écran du code, la liste des fichiers, les photos, les PDF
  et les fenêtres tombaient donc à cheval sur la coupure, et chaque œil n'en
  voyait qu'une moitié. Il fallait sortir les lunettes du mode 3D — dix secondes
  d'écran noir, et parfois des réglages à refaire.

  Désormais un seul geste dessine **toute** l'application deux fois, une par œil :
  **L1 + R1 + Select** à la manette, **Y** au clavier. Le même geste l'éteint, donc
  l'allumer par erreur sur un écran normal ne t'enferme nulle part. Ça se trouve
  aussi dans le menu **Select** et dans **Paramètres → Lunettes XR**.

  Les deux yeux voient la même image : ce n'est pas de la 3D, et c'est justement
  ce qui la rend lisible et reposante.

- **Ce réglage-là ne suit pas d'un appareil à l'autre.** Le Deck avec les lunettes
  le garde allumé, ton iPad et ton laptop ne le voient jamais. Il reste en place
  après un rechargement de la page, et il est déjà là quand l'écran du code
  apparaît.

- **Une vidéo ordinaire reste visible des deux yeux, sans travail en double.** Le
  fichier n'est téléchargé qu'une fois et décodé qu'une fois : l'œil droit reçoit
  une copie de l'image, pas une seconde lecture.

- **Une vidéo 180° garde tout son relief.** C'est la seule chose de l'écran que
  tes deux yeux ne voient pas à l'identique, et c'est voulu : ce genre de fichier
  contient deux images différentes, une par œil, et c'est cette différence qui
  fait la profondeur. Mets le lecteur en côte à côte (touche **V** ou le menu
  **Select**) et chaque moitié de l'écran reçoit son œil, en entier. Le réglage
  « image étirée ou non » n'a plus d'objet dans ce mode et disparaît du menu.

- **Tu règles la vue VR à la manette, en voyant l'image changer.** Maintiens
  **R2** pendant la lecture : le **stick gauche** zoome, le **D-pad gauche/droite**
  ajuste la convergence, le **clic du stick gauche** remet le zoom et celui du
  **stick droit** recentre le regard. Plus besoin d'ouvrir un menu qui recouvre
  justement l'image que tu essaies de juger. Tant que R2 est maintenu, les autres
  boutons ne font rien : la manette pilote la vue et rien d'autre.

- **La convergence est retenue pour chaque fichier.** Si une vidéo te fatigue les
  yeux et que tu l'ajustes, le réglage revient tout seul la prochaine fois que tu
  l'ouvres — et les autres vidéos ne sont pas touchées. C'est voulu : la gêne
  vient de la façon dont la vidéo a été tournée, pas de tes yeux.

- **Tu ne retapes plus ton mot de passe à chaque fois.** Depuis que Hoard demande
  un identifiant, chaque nouvelle fenêtre du navigateur réclamait à nouveau tes
  identifiants, dans une petite fenêtre grise du navigateur — pénible à remplir à
  la manette sur le Steam Deck, et qui n'avait rien à voir avec le reste de Hoard.

  Hoard a maintenant **son propre écran de connexion**, aux mêmes couleurs que le
  reste, et il se pilote entièrement à la manette : le D-pad passe d'un champ à
  l'autre, **A** ouvre le clavier, **A** sur le bouton valide.

  **Tu te connectes une fois, et c'est retenu 30 jours** — un délai qui repart à
  zéro dès que tu utilises Hoard. En usage régulier, tu ne ressaisis donc jamais
  rien. Chaque appareil a sa propre connexion.

  Si ta connexion expire pendant que tu navigues, l'écran revient et **tu reprends
  exactement où tu étais** : le dossier ouvert et la vidéo en cours ne sont pas
  perdus.

  Pour tout déconnecter d'un coup (un appareil perdu, par exemple), il y a un
  moyen côté serveur : voir le guide d'installation, variable `HOARD_SECRET_KEY`.

  À noter : **le code PIN reste une autre chose.** Il verrouille l'écran d'une
  session déjà ouverte sur ton appareil ; la connexion, elle, décide si le serveur
  te répond. Les deux continuent de fonctionner indépendamment.

- **Hoard reconnaît tout seul tes fichiers VR.** Un petit 🥽 apparaît dans la liste
  à côté de ceux qu'il a repérés — au nom du fichier, et à la forme de l'image une
  fois celui-ci ouvert. Il ne bascule pas en mode VR pour autant : le bouton se met
  simplement en évidence, parce qu'ouvrir un fichier pour y jeter un œil ne doit pas
  te catapulter dans une vue de casque.

  En revanche, **le mode que tu choisis est retenu pour ce fichier** et remis en
  place à la réouverture, même depuis une autre machine. Et si Hoard se trompe sur
  un fichier, coupe le mode dessus : il ne te le reproposera plus.

- **Les réglages VR sont dans Paramètres → Player** : champ de vision, vitesse du
  regard à la manette, image étirée ou non, et convergence. Un changement s'applique
  tout de suite, sans recharger la page.

- **Les vidéos VR 180° sont enfin regardables.** Ces fichiers contiennent deux
  images accolées, une par œil, chacune étirée pour couvrir un demi-tour
  d'horizon : affichés tels quels, ils ne ressemblaient à rien. Le bouton 🥽 du
  lecteur (ou la touche **V**) redresse l'image et te laisse regarder autour de
  toi — au doigt, à la souris, ou au stick droit de la manette. Un deuxième appui
  passe en affichage côte à côte, celui qu'attendent des lunettes XR en mode 3D ;
  un troisième revient à l'image normale. **Maj+V** remet le regard au centre.
  Tant que le mode est actif, glisser le doigt sert à regarder et non plus à
  avancer dans la vidéo ou à régler le son, qui restent au clavier, aux boutons et
  au stick gauche.

  Une précision utile : ces fichiers sont très lourds, et Hoard te les envoie sans
  les convertir. C'est donc l'appareil sur lequel tu regardes qui doit savoir les
  lire. Si ça saccade, c'est là qu'est la limite.

- **L'affichage côte à côte est prêt pour des lunettes XR.** Il passe tout seul en
  plein écran et efface les commandes du lecteur pendant ce temps : affichées une
  seule fois sur une image coupée en deux, elles tomberaient à moitié dans chaque
  œil. Tu pilotes à la manette ou au clavier, et tout revient en sortant du mode.
  Si l'image te paraît écrasée ou étirée du double, la touche **B** bascule entre
  les deux façons dont des lunettes lisent ce genre d'image — l'effet se voit tout
  de suite. Un réglage de convergence est disponible dans le menu de la manette,
  à laisser à zéro sauf si un fichier précis te fatigue les yeux.

### Corrigé

- **Le badge en coin affiche maintenant R2**, en plus de L1 et R1. Il ne montrait
  pas la couche VR, alors qu'elle en est une : une gâchette qui n'arrive pas
  jusqu'à Hoard — parce qu'elle est remappée dans la configuration de ta manette,
  par exemple — ressemblait exactement à une gâchette qui arrive.

- **Le stick droit ne sert plus à regarder autour sans maintenir R2.** Il le
  faisait tout le temps, ce qui coûtait le **volume** pendant toute une lecture
  VR : le regard occupait le stick, et le volume n'avait plus où aller. Maintiens
  R2 pour regarder autour, relâche pour régler le volume comme partout ailleurs.

- **Le menu de la manette est enfin lisible en mode côte à côte.** Il s'affichait
  une seule fois, au milieu, donc à cheval sur la coupure entre les deux yeux :
  chacun n'en voyait que la moitié. Le menu **Select** et la carte des boutons
  sont maintenant écrits **une fois par œil**, comme les messages du lecteur
  depuis la version précédente.

- **L'image côte à côte a enfin les bonnes proportions dans les lunettes XR.**
  Sur le Steam Deck avec des Viture Beast, les personnages paraissaient trop
  hauts et trop étroits. Hoard devine maintenant tout seul comment tes lunettes
  consomment l'image, à partir de sa forme : un affichage deux fois plus large
  que la normale — celui qu'il faut régler pour obtenir la 3D — n'a pas besoin
  d'être réétiré, un affichage ordinaire si. Il te dit ce qu'il a deviné par un
  message au moment où le mode s'active, et ton propre choix l'emporte toujours.

- **Les messages du lecteur sont enfin lisibles en mode côte à côte.** Ils
  n'apparaissaient tout simplement pas : écrits une seule fois sur une image
  coupée en deux, ils tombaient à moitié dans chaque œil. Ils sont maintenant
  écrits une fois par œil.

- **Changer la disposition côte à côte se fait à la manette, avec L2.** Il
  fallait jusqu'ici un clavier — que le Steam Deck n'a pas — ou passer par deux
  menus. L2 fait le tour des trois réglages : automatique, étirée, non étirée.
  Le bouton B garde son rôle habituel.

- **Le menu de la manette et la carte des boutons s'adaptent enfin à la taille de
  ton écran.** Sur un affichage très large — celui qu'il faut régler pour obtenir
  la 3D sur des lunettes XR — le menu **Select** occupait deux fois moins de place
  qu'ailleurs et devenait pénible à lire. Il grandit maintenant avec l'écran, et
  son texte avec lui. Rien ne change sur un écran ordinaire ni sur téléphone.

- **La carte des boutons — touche Start — n'est plus un dessin de manette, mais
  une liste.** Le dessin gardait la même petite taille quel que soit l'écran, si bien
  que les noms d'actions écrits autour étaient trop petits pour être lus, même sur
  un écran normal. À la place : la liste de toutes les actions, rangée par couche,
  répartie en autant de colonnes que l'écran est large. Deux commandes qui
  n'apparaissaient nulle part y sont enfin — **L3** coupe le son, **R3** change la
  vitesse de lecture — et les sticks y sont décrits dans le bon sens quand tu as
  inversé les deux. Le **D-pad ↑/↓** fait défiler la liste si elle est plus longue
  que l'écran.

- **La vieille fenêtre grise du navigateur ne s'invite plus avant l'écran de
  connexion.** Elle réapparaissait juste avant, et il fallait l'annuler pour voir
  l'écran de Hoard. Elle ne s'affiche plus du tout : tu vas directement sur
  l'écran de connexion.

- **Le bouton de téléchargement de ta barre de favoris refonctionne.** Depuis que
  Hoard demande un identifiant et un mot de passe, cliquer sur le favori depuis une
  page vidéo ne faisait plus rien d'utile : il annonçait « Site incompatible » et
  ouvrait un onglet, alors que le site n'y était pour rien. Ton navigateur, par
  sécurité, ne transmet pas ton mot de passe Hoard depuis le site de quelqu'un
  d'autre — le favori n'avait donc aucun moyen de prouver que c'était bien toi.

  Il en a un maintenant : **le lien du favori contient un jeton personnel**, qui
  autorise seulement deux choses, lancer un téléchargement et en suivre
  l'avancement. Il ne donne accès ni à tes fichiers, ni à tes réglages. Comme ce
  jeton est dans le lien, **il faut réinstaller le favori** : ouvre les paramètres
  et glisse à nouveau le lien dans ta barre. Si tu diffuses ce lien par mégarde, le
  bouton **🔑 Nouveau jeton** le rend aussitôt inutilisable.

- **Quand quelque chose échoue, le favori te le dit.** La petite fenêtre de suivi
  pouvait rester indéfiniment sur « Analyse de l'URL… » sans jamais rien annoncer.
  Elle affiche désormais ce qui s'est passé : accès refusé (avec la marche à suivre),
  téléchargement en échec, ou suivi interrompu.

- **Le tri de la liste reste celui que tu as choisi.** Passer la liste en « Vu »
  (ou en « Nom », en « Taille »…) tenait jusqu'à la fermeture de Hoard : en
  revenant, tout était retombé sur « Date ». Le tri est maintenant enregistré, et
  retrouvé tel quel à la réouverture — y compris si tu reprends sur la tablette
  après le laptop. Le réglage des paramètres, renommé **Tri de la liste**, affiche
  simplement le tri en cours ; enregistrer les paramètres ne le remet plus à zéro.

## [v2.6.5] — 2026-09-21

### Sécurité

- **Hoard dit maintenant s'il est protégé ou non.** Au démarrage, il affiche
  clairement si un mot de passe est demandé à l'entrée, ou si l'accès est
  ouvert à tous. C'est important si ton Hoard est accessible depuis Internet :
  sans mot de passe, n'importe qui connaissant l'adresse peut voir, déplacer et
  **supprimer** tes fichiers. Rien ne change pour un Hoard utilisé uniquement
  chez toi, sur ton réseau.
- **À savoir : le code PIN ne protège pas contre ça.** Il verrouille l'écran de
  Hoard, ce qui évite qu'on farfouille dans tes fichiers en passant devant la
  tablette. Mais il n'empêche pas d'accéder à Hoard par un autre moyen que son
  interface. Pour ça, il faut le mot de passe d'entrée, décrit dans le guide
  d'installation.
- **Activer le mot de passe ne casse plus la surveillance de Hoard.** Le
  mécanisme qui vérifie que l'application tourne correctement se faisait refuser
  l'entrée et signalait une panne alors que tout allait bien.

## [v2.6.4] — 2026-09-15

### Nouveautés
- **Toute la navigation à la manette, par un seul bouton.** **Select** ouvre un menu qui propose ce qui s'applique là où tu es : le tri (les cinq critères et le sens), le filtrage par tag, créer un dossier, rafraîchir, chercher, l'accueil, les téléchargements, les réglages — et, sur le fichier ou le dossier sélectionné, l'ouvrir, le renommer, le tagger, l'épingler, le déplacer, le supprimer ou le marquer vu. D-pad pour parcourir, A pour valider, B pour fermer. Jusqu'ici la barre de tri et les boutons de ligne n'étaient accessibles qu'au doigt ou à la souris.
- **Le même menu pendant la lecture** : **Select** l'ouvre aussi quand une vidéo est en cours, avec ce qui sert là — régler le départ du dossier, marquer vu, les sous-titres, l'affichage, la vitesse, l'export des segments, renommer, déplacer, supprimer, fermer. Le réglage **⏱ Départ du dossier** n'était atteignable qu'au doigt ou à la souris : c'était le dernier bouton de Hoard dans ce cas.
- **Marquer un média vu ou non vu sans l'ouvrir** : dans le menu, ou avec **X** directement sur la liste. Pratique pour un film déjà vu ailleurs, ou pour repartir de zéro sur une série. Marquer « non vu » efface aussi la position de lecture, pour ne pas reprendre au milieu d'un fichier affiché comme jamais ouvert.

- **Nouveau tri « Vu »** dans la barre de tri : il classe par date du dernier visionnage. Un dossier remonte en tête dès que tu regardes une vidéo **quelque part en dessous**, même enfouie dans plusieurs sous-dossiers — ce que le tri « Date » ne pouvait pas faire, puisqu'il montre la date des fichiers sur le disque et que regarder une vidéo ne change rien sur le disque. Les deux tris coexistent : « Date » pour voir ce qui vient d'arriver, « Vu » pour retrouver où tu en étais. Ce que tu n'as jamais ouvert est regroupé en fin de liste.

### Corrections
- **Un fichier du même nom à destination ne bloque plus le déplacement.** Déplacer une vidéo vers un dossier qui contenait déjà ce nom pouvait laisser le déplacement « en cours » indéfiniment, sans message ni résultat. Hoard demande maintenant quoi faire : **Écraser** remplace définitivement le fichier qui s'y trouvait, **Annuler** ne touche à rien. La fenêtre se pilote à la manette comme au clavier, et démarre sur *Annuler*. Au passage, un fichier ne peut plus être remplacé sans qu'on l'ait demandé — ce qui pouvait arriver en silence jusqu'ici.
- **Un dossier déplacé emporte tout ce qu'il contient**, progression de lecture et tags compris. Jusqu'ici ils étaient perdus. Les tags survivent aussi à un renommage, et supprimer un dossier ne laisse plus traîner les informations de son contenu.
- **La sélection à la manette est enfin visible dans toutes les fenêtres.** Dans huit d'entre elles — tags, renommage, nouveau dossier, parcourir, sélecteur de destination, téléchargements, code PIN — le curseur se déplaçait sans rien afficher : on validait à l'aveugle.
- **La manette ne traverse plus les fenêtres.** Quand une fenêtre était ouverte (tags, renommage, nouveau dossier, téléchargements…), la manette continuait de piloter la liste **derrière** : le D-pad y déplaçait une sélection invisible et A pouvait ouvrir un fichier par-dessous. Ces fenêtres se parcourent maintenant à la manette, et **B** les ferme. L'écran de code PIN se saisit lui aussi à la manette.
- **Plus de boutons qui ne répondent pas** dans la liste de fichiers : quatre d'entre eux étaient associés à des commandes du lecteur vidéo et ne faisaient rien tant qu'aucune vidéo n'était ouverte. **Start** réaffiche la carte des boutons, qui était devenue inaccessible depuis la liste.

## [v2.6.0] — 2026-08-25

### Nouveautés
- **Relancer un téléchargement depuis l'historique** : un bouton **↻** sur chaque ligne remet la même vidéo en file d'attente. C'est la réponse aux vidéos perdues : le fichier n'est pas récupérable, mais son adresse est toujours dans l'historique, donc un clic suffit pour retenter. Hoard conserve désormais aussi la page d'origine du téléchargement, sans quoi beaucoup de sites refuseraient la relance. Si tu relances quelque chose qui avait déjà réussi, Hoard prévient : tu obtiendras un second fichier à côté du premier.
  - À savoir : les cookies de ta session ne sont pas conservés (ce sont des identifiants). Pour les sites qui demandent une connexion, c'est le fichier `cookies.txt` des réglages qui prend le relais.

### Améliorations
- **Boutons plus faciles à toucher** dans l'historique des téléchargements : les icônes ↻ et ✕ étaient minuscules, leur zone de clic est maintenant confortable au doigt.

## [v2.5.2] — 2026-08-25

### Corrections
- **Un site qui ne répond plus ne bloque plus la file** : si un serveur acceptait la connexion puis se taisait, le téléchargement restait suspendu pour toujours — et comme Hoard télécharge un fichier à la fois, tous les suivants attendaient derrière sans jamais démarrer. Un délai d'attente est désormais appliqué (30 secondes de silence), après quoi le téléchargement échoue proprement et la file repart.
- **Le bouton « Parcourir… » pour choisir le dossier de téléchargement ne répondait pas** : la fenêtre de sélection s'ouvrait bel et bien, mais **derrière** la page des réglages — donc invisible. Et même au premier plan elle serait apparue vide lorsque le dossier configuré n'existait pas encore. Les deux sont corrigés : la fenêtre passe devant, et si le dossier est introuvable elle revient à la racine en le signalant.

## [v2.5.1] — 2026-08-25

### Corrections
- **Des vidéos disparaissaient alors que Hoard affichait « Terminé »** — c'était la cause des pertes. La bookmarklet donne au fichier le titre de la page web ; or un même site donne souvent le même titre à toutes ses vidéos. Dès qu'un fichier de ce nom existait, l'outil de téléchargement **abandonnait sans rien dire**, et Hoard affichait quand même la barre à 100 % puis « Terminé ». La vidéo n'était nulle part. Désormais Hoard numérote les doublons — `Ma video.mp4`, puis `Ma video (2).mp4` — comme le fait un navigateur, et surtout il **vérifie que le fichier existe** avant d'annoncer un succès : en cas de problème, l'entrée passe en échec avec un message qui explique quoi faire.
- **Savoir où atterrissent les téléchargements** : le dossier de destination est créé tout seul, donc une adresse mal saisie ne provoquait aucune erreur — elle créait simplement un dossier ailleurs, où tout s'accumulait sans prévenir. Hoard affiche maintenant le **chemin complet** de destination, dans la fenêtre de téléchargement comme dans les réglages, signale quand le dossier n'existe pas encore, et permet de le choisir en naviguant (bouton **Parcourir…**) au lieu de le taper.
- **Nom de fichier trompeur** : pour certaines vidéos, l'historique affichait un nom en `.mp4` alors que le fichier écrit portait une autre extension — « Aller au fichier » ne trouvait alors rien. Le nom affiché est maintenant celui du vrai fichier.
- **Titres contenant un `%`** : ils produisaient un nom de fichier abîmé (« Best of 50%(off) deal » devenait « Best of 50NAeal »). C'est corrigé.

## [v2.5.0] — 2026-08-24

### Nouveautés
- **Historique des téléchargements** : le bouton 📥 garde maintenant la trace de **tout** ce que tu as téléchargé, avec la date et le résultat. Jusqu'ici la liste s'effaçait au bout d'une heure et à chaque redémarrage du NAS : un téléchargement raté ne laissait aucune trace, impossible de savoir s'il avait échoué ou n'était jamais parti. Les échecs affichent désormais leur cause, et un bouton **Aller au fichier** ouvre le dossier du fichier téléchargé. L'historique est conservé sans limite de durée.
- **Consulter le journal depuis Hoard** : **Paramètres → Maintenance → Journal** affiche l'activité du serveur des **30 derniers jours** (téléchargements, erreurs, redémarrages), avec filtre par niveau et bouton de copie. Plus besoin d'ouvrir Portainer pour comprendre ce qui s'est passé.
- **Redémarrer Hoard depuis les réglages** : un bouton **↻ Redémarrer Hoard** dans **Paramètres → Maintenance** relance l'application sans passer par le NAS. Si un téléchargement est en cours, Hoard prévient avant. La page se recharge toute seule une fois le serveur revenu.

### Corrections
- **Téléchargements qui restaient bloqués « en attente » pour toujours** : quand un téléchargement plantait d'une certaine façon, le mécanisme qui traite la file s'arrêtait définitivement — sans le dire. Tous les téléchargements suivants restaient alors en attente indéfiniment, sans jamais démarrer ni signaler d'erreur, jusqu'au redémarrage du NAS. C'est corrigé : un téléchargement en échec affiche désormais son erreur, et les suivants s'enchaînent normalement.
- **Bookmarklet de téléchargement sur certains sites** : sur des sites qui bloquent les requêtes vers un site externe (fréquent sur les sites de streaming chargés de publicités), la bookmarklet affichait juste « Hoard non joignable » sans solution. Elle ouvre désormais automatiquement Hoard dans un nouvel onglet pour terminer le téléchargement dans ce cas.
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
