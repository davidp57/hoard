# BL-104 — Faisabilité du client natif

Status: ⬜ ready
Type: spike
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Files: `client/` (nouveau), `.github/workflows/`

## What to build

Une application Flutter **minimale** — lister un dossier, lire une vidéo, remonter la
progression — dont le seul but est de **trancher trois inconnues** avant qu'on
n'engage l'interface complète. Ce n'est pas le socle du client : c'est un instrument de
mesure, et son code a vocation à être jeté ou refondu.

Les trois inconnues, par ordre de gravité :

1. **libmpv sous Flutter.** `media_kit` ne livre pas de libmpv précompilé pour Linux
   ([#638](https://github.com/media-kit/media-kit/issues/638),
   [#1055](https://github.com/media-kit/media-kit/issues/1055)) et s'attend à le trouver
   dans le système. SteamOS étant en lecture seule, il faut l'embarquer. À vérifier sur
   x86_64 ; l'ARM64 est reporté au ticket 12 (le Frame n'est pas encore livré).
2. **Décodage matériel réel.** Sur l'APU AMD du Deck, VAAPI est réputé acquis — mais
   réputé n'est pas mesuré, et c'est la justification principale du lot.
3. **Saisie de texte en mode Gaming.** Le défaut visé touche les applications
   non-Steam en général, pas seulement Edge : il faut observer ce qu'une application
   Flutter native subit, et vérifier qu'un champ piloté par un clavier maison à la
   manette y échappe.

### Périmètre fonctionnel

- Adresse du serveur saisissable et mémorisée.
- Liste à plat d'un dossier via `/api/files?path=`, sans mise en forme soignée. Les
  chemins sont relatifs à `MEDIA_ROOT` (`safe_path`) ; `/api/browse` ne sert qu'au
  sélecteur de racine côté serveur et n'est pas utilisé ici.
- Lecture d'un fichier via `/api/file?path=` avec `media_kit`, reprise à la position
  lue sur `GET /api/progress?path=` et sauvegarde par `POST /api/progress?path=`
  (corps `{position, duration, cut_in, cut_out}`) en fin de lecture.
- Un champ de saisie ordinaire **et** un champ servi par un clavier à l'écran
  rudimentaire piloté à la manette — les deux côte à côte, pour comparer.
- Un écran de diagnostic affichant la valeur de `hwdec` retenue par mpv, le codec, et
  la résolution.

### Chaîne de compilation

Le SDK Flutter n'est présent sur aucune machine. Décisions retenues :

- **Windows** : SDK Flutter natif, pour itérer vite — c'est aussi une cible réelle.
- **Linux x86_64** : SDK Flutter dans **WSL2** (déjà installé), plutôt que Docker
  (absent) ou une compilation sur le Deck lui-même.
- **Linux ARM64** : reporté au ticket 12, via la CI.

## Mesures à produire

Le décodage matériel se prouve par une **différence**, pas par un chiffre isolé : on
relève la charge processeur **avec** et **sans** accélération sur le même fichier, par
un delta sur un intervalle d'au moins 30 s de lecture — jamais par un compteur cumulé
divisé par une durée.

| Mesure | Comment | Ce qu'on en conclut |
|---|---|---|
| `hwdec` effectif | écran de diagnostic, propriété mpv | `no` → l'accélération ne prend pas |
| Charge CPU `--hwdec=auto` vs `--hwdec=no` | delta sur ≥ 30 s, même fichier HEVC 1080p | écart faible → l'accélération n'apporte rien |
| Formats | un HEVC 10 bits, un MKV piste DTS, des sous-titres ASS | lecture ou échec |
| Saisie mode Gaming | champ ordinaire, `Steam+X` puis menu d'accès rapide | quel clavier s'ouvre, le texte arrive-t-il |
| Saisie clavier maison | champ servi par le clavier à la manette | indépendance vis-à-vis du système |

## Acceptance criteria

- [ ] L'application se compile et tourne sur Windows et sur Linux x86_64
- [ ] Elle liste un dossier réel du NAS et lit une vidéo depuis `/api/file`
- [ ] La progression écrite par le client est visible dans l'interface web, et
      réciproquement
- [ ] libmpv est **embarquée** dans le paquet Linux, sans dépendre d'une bibliothèque
      installée sur la machine hôte
- [ ] Le tableau de mesures ci-dessus est rempli, sur le Deck, avec les valeurs relevées
- [ ] Le clavier maison permet de saisir un texte à la manette, en mode Gaming, sans
      recourir au clavier Steam
- [ ] Un compte rendu conclut : on continue tel quel, on continue avec réserves, ou on
      revoit le choix de techno — avec les chiffres à l'appui

## Résultats — poste de développement (2026-09-21)

Environnement : Ubuntu 24.04 sous WSL2, Flutter 3.47.5, Dart 3.13.4. La
compilation depuis `/mnt/d` prend 50 s, ce qui ne justifie pas de déplacer les
sources hors du dépôt.

**Inconnue 1 — libmpv : levée, mais pas comme annoncé en amont.**

Le paquet produit par `flutter build linux --release` pèse 25 Mo et ne contient
**pas** libmpv : seulement `libapp.so`, `libflutter_linux_gtk.so` et deux plugins
de 15 et 47 Ko. Le mécanisme exact, qui n'est nommé dans aucune des issues amont :

- `libmedia_kit_video_plugin.so` déclare `NEEDED libmpv.so.2`, et son `RUNPATH`
  est le **chemin absolu de la machine de compilation**
  (`…/client/linux/flutter/ephemeral`). Sur toute autre machine, ce chemin
  n'existe pas et le chargement se rabat silencieusement sur la libmpv système.
- `hoard_client` porte bien `RUNPATH $ORIGIN/lib`, mais ne déclare aucune
  dépendance à libmpv : ce `RUNPATH` ne sert donc à rien ici, et `DT_RUNPATH`
  ne se transmet pas aux bibliothèques chargées ensuite.
- `LIBMPV_LIBRARY_PATH`, que `media_kit` documente, **n'y change rien** : elle
  est lue par le code Dart, donc bien après que l'éditeur de liens a refusé de
  démarrer. C'est pourquoi le contournement qui circule ne fonctionne pas.

Vérifié en masquant la libmpv système (montage de `/dev/null` dans un espace de
noms utilisateur, sans droits administrateur) :

| Lancement | Résultat |
|---|---|
| tel quel, copie présente dans `bundle/lib` | l'application ne démarre pas |
| `LIBMPV_LIBRARY_PATH` seul | l'application ne démarre pas |
| `LD_LIBRARY_PATH=<bundle>/lib` | démarre, et **seule** la libmpv du paquet est chargée |

Parade retenue pour le spike : un lanceur `run.sh` qui pose `LD_LIBRARY_PATH`.
Parade propre pour le lot : corriger le `RUNPATH` du plugin (`patchelf --set-rpath
'$ORIGIN'`), ou empaqueter en Flatpak, qui place libmpv sur un chemin standard de
son bac à sable et rend la question sans objet.

**Inconnues 2 et 3 — non mesurables ici.** WSLg n'expose pas VAAPI, et il n'y a
pas de mode Gaming. Elles se mesurent sur le Deck, avec l'archive produite.

**Réserve sur l'archive de test.** Elle embarque libmpv et sa fermeture de
dépendances prise sur Ubuntu, en excluant le runtime C et tout ce qui touche à
l'affichage, au GPU et au son — qui doivent rester ceux de l'hôte, faute de quoi
le décodage matériel qu'on vient mesurer ne fonctionnerait pas. C'est un montage
jetable, acceptable pour une mesure, et précisément ce que le Flatpak supprime.

## Mode opératoire sur le Deck

Le test se fait **en mode Gaming**, qui est le contexte réel — et où il n'y a
pas de terminal. L'application prend donc elle-même toutes les mesures et
affiche le verdict à l'écran ; rien n'est à lire dans une console, rien n'est à
relancer avec une variable d'environnement. Le mode Bureau ne sert qu'à
l'installation, une fois.

### Préparation (mode Bureau, une seule fois, sans terminal)

0. Produire l'archive : `flutter build linux --release` puis
   `client/tools/package-linux.sh <dossier-de-sortie>`.
1. Copier `hoard-spike.tar.gz` (~105 Mo) sur le Deck.
2. Dans le gestionnaire de fichiers : clic droit → extraire. On obtient un
   dossier `hoard-spike`.
3. Ouvrir `run.sh` dans l'éditeur de texte et corriger la ligne `HOARD_URL`
   avec l'adresse du serveur Hoard. Elle pré-remplit le champ d'adresse — sans
   quoi un échec des deux claviers rendrait tout le reste du test inatteignable.
4. Steam → *Ajouter un jeu* → *Ajouter un jeu non-Steam* → *Parcourir* → passer
   le filtre sur *Tous les fichiers* → choisir `run.sh`.

### Test (mode Gaming)

Lancer « run.sh » depuis la bibliothèque. Trois choses à observer, dans l'ordre :

**Clavier.** L'écran d'accueil porte deux champs. Le **A** est un champ
ordinaire servi par le clavier du système : essayer `Steam+X`, puis le menu
d'accès rapide. Le **B** est servi par le clavier maison, piloté à la
croix directionnelle. C'est la comparaison qui compte, pas chaque champ
isolément.

**Navigation.** Se connecter, parcourir à la croix directionnelle (A pour
ouvrir, B pour remonter), choisir une vidéo — de préférence un HEVC 1080p ou
plus, c'est là que l'écart de décodage se voit.

**Décodage.** Dans le lecteur, un bouton *Compare hardware vs software
decoding*. Il joue le même passage deux fois, une fois par décodeur, laisse
5 s de stabilisation à chaque fois (un saut et un remplissage de tampon
coûtent du processeur qui n'a rien à voir avec le décodage), mesure 25 s, et
affiche un verdict en clair : décodeur retenu, charge dans les deux cas, et le
rapport entre les deux. Compter une minute, en laissant tourner.

La mesure est un **delta** de `/proc/self/stat` sur l'intervalle, pas un
compteur cumulé divisé par une durée — ce dernier décrirait la moyenne depuis
le lancement, pas la charge pendant la lecture. L'unité est le pourcentage d'un
cœur, comme `top` : 400 % signifie quatre cœurs saturés.

## Notes

Ce ticket est une **porte**. Les tickets 02 à 12 ne sont volontairement pas détaillés
tant qu'il n'est pas rendu : si la mesure 2 échoue, la justification principale du lot
tombe ; si la mesure 1 échoue, le choix de `media_kit` est à reprendre.

David teste en parallèle le contournement clavier documenté (ouvrir le clavier depuis
le **menu d'accès rapide** plutôt que par `Steam+X`) sur son usage actuel. Son résultat
ne conditionne pas le lot, qui se fait de toute façon, mais il renseigne la mesure 5.
