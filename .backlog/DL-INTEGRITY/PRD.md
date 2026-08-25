# Lot DL-INTEGRITY — Un téléchargement « terminé » doit exister

Status: ✅ done
Branch: fix/download-destination-and-skip → PR → develop

## Problem Statement

Constat utilisateur : « un download lancé depuis la bookmarklet, arrivé dans la
file, téléchargé et présent dans l'historique, mais nulle part dans le dossier de
destination — j'ai perdu des tas de vidéos comme ça. »

L'enquête a trouvé **deux causes distinctes**, toutes deux reproduites.

### 1. Le fichier est ailleurs que là où l'utilisateur le cherche

`start_download` fait `output_dir.mkdir(parents=True, exist_ok=True)` : Hoard
**crée** le dossier de destination s'il n'existe pas, sans rien signaler. Le réglage
*Dossier de téléchargement* est un champ texte libre ; une valeur de travers crée un
dossier fantôme où tout atterrit. Constaté en production : les téléchargements
partaient dans un dossier `[[_downloads` que l'utilisateur ne reconnaissait pas et
dont l'interface n'affiche que le nom relatif — jamais le chemin complet.

### 2. yt-dlp saute le téléchargement quand le nom est déjà pris, et Hoard dit « terminé »

La bookmarklet envoie `document.title` comme nom de fichier. Sur un site donné,
plusieurs vidéos partagent souvent le même titre de page. Quand le fichier cible
existe déjà, yt-dlp **ne télécharge pas** et ne lève **aucune exception**.

Reproduit avec deux vidéos différentes et un même titre :

| Étape | Fichier sur disque | Statut du job |
|---|---|---|
| `sample-10s.mp4` (5 485 935 o) | `Collision.mp4` = 5 485 935 o | ✓ terminé |
| `sample-15s.mp4` (**11 916 526 o**) | `Collision.mp4` = **5 485 935 o, inchangé** | ✓ terminé |

La seconde vidéo n'est **jamais écrite**. Pire, le hook de progression émet quand
même un événement `finished` : la barre atteint 100 %, le job passe `done` et
l'historique affiche « Terminé ». Aucun signal, nulle part.

Signal discriminant mesuré : un vrai téléchargement émet des événements
`downloading` (13 dans le test), un skip en émet **zéro** tout en émettant
`finished`.

### Défauts annexes trouvés en chemin

- **Le nom stocké peut ne pas exister** : le code force l'extension
  `merge_output_format` (`.mp4`) sur le nom final, même quand yt-dlp n'a pas
  fusionné et a écrit un `.webm` / `.mkv`. L'historique annonce alors un fichier
  absent et « Aller au fichier » ne trouve rien.
- **Le titre est injecté dans un template yt-dlp** sans échappement :
  `_sanitize_filename` retire les caractères interdits mais pas le `%`. Vérifié :
  le titre `Best of 50%(off) deal` produit le fichier `Best of 50NAeal.mp4`.
- **« Terminé » n'est jamais vérifié** : rien ne constate l'existence du fichier
  avant de déclarer le succès.

## Solution

Principe directeur : **Hoard ne doit jamais annoncer un succès qu'il n'a pas
constaté, ni écrire un fichier à un endroit que l'utilisateur ne voit pas.**

- Garantir un nom de fichier libre avant de lancer yt-dlp ; en cas de collision,
  suffixer ` (2)`, ` (3)`… comme le fait un navigateur.
- Détecter le skip (zéro événement `downloading`) et le remonter comme une erreur
  explicite au lieu d'un faux succès.
- Vérifier l'existence du fichier final avant de passer le job en `done`.
- Prendre le nom réel chez yt-dlp (`requested_downloads[0].filepath`) plutôt que de
  le reconstruire.
- Échapper les `%` du titre.
- Rendre la destination lisible : chemin complet affiché, avertissement quand le
  dossier n'existe pas encore, sélection par navigation plutôt que saisie libre.

## User Stories

1. En tant qu'utilisateur, je veux qu'un téléchargement marqué « terminé » ait
   réellement produit un fichier, pour ne plus découvrir des pertes après coup.
2. En tant qu'utilisateur, je veux savoir exactement où mes téléchargements
   atterrissent, pour les retrouver depuis le NAS comme depuis Hoard.
3. En tant qu'utilisateur, je veux que deux vidéos de même titre donnent deux
   fichiers, pas une seule.

## Implementation Decisions

- **Nom libre calculé côté Hoard**, pas côté yt-dlp : aucune option yt-dlp ne
  propose « renommer en cas de collision » (`overwrites` ne sait qu'écraser ou
  sauter). Le nom candidat est testé sur le préfixe `stem + "."` pour couvrir
  toutes les extensions possibles, l'extension n'étant pas connue à l'avance.
- **Pas de `glob()` pour ce test** : un stem peut contenir `[`, métacaractère glob
  (le dossier `[[_downloads` de production l'illustre). Comparaison de noms via
  `iterdir()`.
- **Le compteur `downloading` reste un filet**, pas la protection principale : le
  nom libre supprime la cause. Il couvre le cas où aucun titre n'est fourni et où
  le nom ne peut donc pas être anticipé.
- **Le dossier reste créé automatiquement** (le supprimer casserait le premier
  usage), mais sa création est journalisée et l'interface prévient à l'avance.

## Testing Decisions

- Test de non-régression du scénario exact : deux téléchargements de contenus
  différents avec le même titre doivent produire deux fichiers distincts.
- Un skip simulé (zéro événement `downloading`) doit produire un job `error`, pas
  `done`.
- Un fichier final absent doit produire un job `error`.
- Les tests n'accèdent pas au réseau : yt-dlp est simulé, comme dans les tests
  existants.

## Out of Scope

- Relancer un téléchargement depuis une entrée d'historique (proposé, non retenu
  pour ce lot — l'historique conserve les URL, donc ça reste faisable plus tard).
- Récupération des fichiers déjà perdus : impossible côté Hoard, ils n'ont jamais
  été écrits.

## Further Notes

Lockstep doc : `docs/user-guide.*.md` (destination, collisions), `docs/developer.*.md`
(cycle de vie du téléchargement), `CHANGELOG.md` + `docs/changelog-user.fr.md`.

## Déjà livré dans ce lot

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-079 | Un téléchargement « terminé » doit avoir produit un fichier | fix | ✅ done |
| BL-080 | Savoir où atterrissent les téléchargements | fix | ✅ done |
| BL-081 | Le test de redémarrage peut tuer le lanceur de tests | fix | ✅ done |
| BL-082 | Le bouton « Parcourir… » ne fait rien (correctif de suivi de BL-080) | fix | ✅ done |
