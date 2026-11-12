---
status: accepted
date: 2026-09-21
---

# Client natif : Flutter + libmpv, cibles Linux x86_64 / Linux ARM64 / Windows

Hoard se consulte aujourd'hui depuis un navigateur. Sur **Steam Deck en mode Gaming**,
cet usage se dégrade : la saisie au clavier ne fonctionne pas de façon fiable, et le
moteur web décode la vidéo moins bien qu'un lecteur dédié. On ajoute un **client natif**
qui parle à l'API HTTP existante, sans rien changer au serveur.

Le besoin s'étend à trois machines : le Steam Deck (x86_64), le **Steam Frame**
(Snapdragon 8 Gen 3, donc **ARM64**, commandé) et le laptop Windows tactile. L'iPad
reste une cible possible, non engagée.

## Décision

**Flutter (Dart) + `media_kit`**, qui embarque **libmpv**, compilé nativement pour
chaque cible. Le client couvre le périmètre complet de l'interface web — navigation,
lecture vidéo, galerie, archives, tags, téléchargements, segments, réglages.

Conséquences directes de ce choix :

- **Le serveur ne change pas.** Le client consomme l'API existante ; `/api/file` sert
  le fichier brut avec `Range`, donc mpv lit sans transcodage et `/api/transcode`
  devient inutile pour ce client.
- **La saisie de texte ne dépend pas du clavier Steam.** Le client dessine son propre
  clavier à l'écran, piloté à la manette. Le défaut visé
  ([steam-for-linux#9117](https://github.com/ValveSoftware/steam-for-linux/issues/9117))
  touche les applications non-Steam en mode Gaming en général, pas seulement Edge :
  s'en remettre au clavier du système reconduirait le problème dans le client.
- **Distribution par Flatpak.** SteamOS est en lecture seule et se réécrit à chaque
  mise à jour, donc aucune dépendance système durable. Le Flatpak est aussi la réponse
  au fait que `media_kit` ne livre **pas** de libmpv précompilé pour Linux
  ([#638](https://github.com/media-kit/media-kit/issues/638),
  [#1055](https://github.com/media-kit/media-kit/issues/1055)) : le paquet embarque la
  sienne, pour x86_64 comme pour ARM64.
- **Le dépôt gagne une chaîne de compilation.** Cela invalide deux règles de
  `CLAUDE.md` — « no build step » et « le frontend est un fichier unique » — qui ne
  valent désormais que pour `frontend/`.

## Alternatives écartées

**Binaire Windows x86 exécuté par Proton.** Techniquement possible sans double amorçage :
le code x86_64 s'exécute directement sur le processeur du Deck, Proton ne traduit que
les appels Windows. Écarté pour deux raisons. D'abord, Proton s'intercale sur le
sous-système d'entrée, c'est-à-dire précisément celui qu'on cherche à réparer. Ensuite,
le Frame étant ARM64, un `.exe` y empilerait **FEX** (traduction x86→ARM) *et* Proton
sous un décodeur vidéo. Le bénéfice serait nul : Flutter compile nativement les trois
cibles depuis la même base.

**Tauri.** La réponse réflexe à « application native en Rust » affiche la page dans
WebKitGTK sous Linux — un moteur web moins capable qu'Edge pour la vidéo, à
l'accélération matérielle capricieuse. On réécrirait l'application pour hériter des
mêmes défauts en pire.

**Rust (Slint ou egui) + libmpv.** Bon choix pour un périmètre réduit, mais sur le
périmètre complet il faudrait construire ce que Flutter fournit : listes virtualisées,
champs de saisie, dialogues, lecteur PDF, lecture d'archives, et le câblage du rendu
mpv dans une texture. Slint n'ouvre pas non plus la cible iPad.

**Kodi et un add-on.** L'interface existe et convient à la manette, mais c'est celle de
Kodi ; la gestion de fichiers propre à Hoard s'y greffe mal.

**Ne rien faire — navigateur en mode kiosque.** Supprime les barres et stabilise le
plein écran pour une soirée de travail, mais ne touche ni les codecs, ni le décodage
matériel, ni la batterie. Retenu comme palliatif immédiat, pas comme solution.

## VR immersive : une application distincte, plus tard

Le Frame projette n'importe quelle application 2D sur un écran virtuel géant
(*Theatre Mode*) sans aucun travail spécifique : compiler en ARM64 suffit. C'est le
périmètre engagé.

La lecture de films **SBS 180°/360°** est un besoin réel mais différé, et elle ne se
fera **pas** en Flutter : elle demande un rendu OpenXR stéréo, hors de portée du
toolkit. Elle fera l'objet d'une application séparée, vraisemblablement en Rust
(`openxr` + `wgpu`).

Ce n'est pas un travail perdu : les deux applications ne partagent que le client d'API,
soit quelques centaines de lignes. On écarte donc explicitement l'idée d'un noyau commun
appelé depuis Dart par FFI, qui paierait la complexité d'un pont pour mutualiser la
partie la moins chère.

## Révision 2026-09-21 — ce que le spike a mesuré

Le ticket BL-104 a tourné sur un Steam Deck réel. Les trois risques ouverts
ci-dessous sont levés, et un quatrième est apparu, plus gênant qu'eux tous.

**Ce qui est confirmé.** Le décodage matériel fonctionne : `hwdec=auto-safe`
donne `vaapi-copy`, à 102 % d'un cœur contre 118 % en logiciel — c'est le mode
retenu. Forcer `hwdec=vaapi` est **contre-productif** : le partage de mémoire
GPU n'existe pas avec la texture Flutter, mpv refuse et retombe en logiciel.
La saisie au clavier Steam fonctionne dans une application native, ce qui règle
la motivation première du lot. libmpv s'embarque, via une liste blanche mesurée
sur la cible et non une liste noire.

**La réserve, et elle est sérieuse : `media_kit` ne signale pas ses images à
Flutter.** La vidéo n'avance que quand l'interface est repeinte pour une autre
raison : 8 images par seconde au repos, 25 dès qu'une animation tourne. Mesuré,
et contourné en forçant un redessin à chaque trame — ce qui fait dessiner la
machine en permanence et se paie en batterie sur une console portable.

Ça ne remet pas en cause **Flutter**, qui tient : c'est la brique vidéo qui est
en cause. Deux voies pour le ticket 04, à trancher avec une mesure et non sur
le papier :

- **mpv dessine sa propre surface**, l'interface Flutter est disposée autour ou
  par-dessus. Supprime le problème à la racine, au prix d'une composition plus
  délicate — et c'est la voie que prennent les lecteurs qui marchent.
- **Garder la texture, forcer le redessin pendant la lecture seulement.**
  Immédiat, quelques lignes, mais on paie la batterie tant que la vidéo joue.

Si aucune des deux ne convainc, la question remontera au choix de `media_kit`
lui-même, pas à celui de Flutter.

## Risques ouverts (état initial, voir la révision ci-dessus)

- **Décodage matériel sur le Frame.** Sur le Deck, mpv + VAAPI sur l'APU AMD est acquis.
  Sur un GPU Adreno sous Linux, le décodage vidéo matériel est historiquement partiel et
  reste **à mesurer**. Non bloquant pour le Deck ; à lever avant d'engager la cible Frame.
- **`media_kit` sur Linux ARM64.** Compilation et empaquetage à valider ; issues amont
  connues ([#682](https://github.com/media-kit/media-kit/issues/682)).
- **Clavier en mode Gaming.** Le clavier maison lève le risque par construction, mais le
  comportement d'une application native non-Steam reste à observer.

Ces trois points sont l'objet du ticket de faisabilité, à traiter **avant** d'écrire
l'interface.

## Conséquences

- Nouveau répertoire `client/` à côté de `backend/` et `frontend/`.
- La CI gagne la compilation Flutter ; les durées passent de secondes à minutes.
- L'interface web reste maintenue : elle sert l'iPad et tout navigateur, et reste le
  seul accès tant que le client ne couvre pas le périmètre.
- Le client porte sa **propre version**, indépendante de `pyproject.toml`, et annonce au
  démarrage la version d'API qu'il sait parler.
