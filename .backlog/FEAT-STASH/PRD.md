# Lot FEAT-STASH — Hoard trie et lit, Stash garde et décrit

Status: ⬜ ready

## Problem Statement

David a installé Stash sur le NAS (2026-11-22).
Il garde Hoard pour regarder ses vidéos, mais veut un dossier dédié aux vidéos qu'il garde, et que ce soit Stash qui gère ce dossier.
Il veut **envoyer** une vidéo de Hoard vers Stash, avec des métadonnées, et **retrouver** dans Hoard les vidéos de Stash avec ce que Stash sait d'elles.

Le partage des rôles : Hoard parcourt `downloads`, lit et trie ; Stash garde la collection et la décrit.

## Ce qui est établi (2026-11-22)

- **Stash v0.32.0** (sortie le 2026-11-02), API GraphQL sur `/graphql`.
- **Instance de David** : `127.0.0.1:9999` sur le NAS, identifiants activés (`/` renvoie vers `/login`, `/graphql` répond 401 sans clé). Version installée et dossiers indexés non lus faute de clé.
- **Clé d'API** : en-tête `ApiKey` ou paramètre `?apikey=` (`internal/api/authentication.go`). Elle se crée dans Stash, *Settings → Security*.
- **Schéma** (`graphql/schema/schema.graphql`, `types/scene.graphql`, `types/metadata.graphql`) :
  - lecture : `findScenes` (filtre par chemin), `findScene`, `findJob` ;
  - scène : `resume_time`, `play_count`, `play_duration`, `last_played_at`, `o_counter`, `rating100`, `organized`, `tags`, `performers`, `studio`, `scene_markers`, `interactive`, `files`, `paths` ;
  - écriture : `metadataScan(input: {paths})` scanne des chemins précis et rend un id de job ; `metadataIdentify(input: {sources, sceneIDs})` identifie des scènes précises ; `sceneUpdate` ; `sceneSaveActivity(id, resume_time, playDuration)` ; `sceneAddPlay(id)` ; `moveFiles` ; `deleteFiles` ; `sceneDestroy(delete_file, delete_generated)`.
- **Médias générés**, sous `/scene/{id}/` : `screenshot`, `preview` (mp4), `webp`, `vtt/thumbs` + `vtt/sprite` (vignettes de la barre de lecture), `vtt/chapter` (markers), `funscript`, `interactive_heatmap`, `caption`.
- **Pas d'API HereSphere ni DeoVR dans le cœur de Stash** (rien dans `internal/api`). Hoard sert déjà HereSphere (FEAT-HERESPHERE), mais envoie aujourd'hui `tags: []`, ni vignette ni script.
- **Réponses de David (2026-11-22)** : le dossier dédié n'existe pas encore, on le crée ; aucune source d'identification (stash-box, scrapers) n'est configurée, il attend la fin du premier scan ; il n'utilise pas les tags de Hoard (`file_tags`).

## Solution

Hoard se connecte à Stash par son API, avec une clé gardée côté serveur.
Une action « Envoyer à Stash » déplace la vidéo dans le dossier de Stash, la fait scanner, et y recopie la position de reprise et l'état « vu ».
Pour les vidéos de ce dossier, Hoard affiche ce que Stash sait (vignette, performers, studio, tags, note, markers) dans la liste, dans le lecteur et dans HereSphere, et recopie la progression dans Stash.
Dans ce dossier, déplacer et supprimer passent par Stash, pour que Stash ne perde pas ses métadonnées.
Sans réglage Stash, Hoard marche exactement comme aujourd'hui.

## Décisions (Claude, 2026-11-22 — valent par défaut)

1. **Le dossier de Stash est un sous-dossier de la racine de Hoard**, par défaut `_stash` (soit `/volume1/downloads/_stash` sur le NAS).
   Raison : un déplacement à l'intérieur d'un même montage Docker est un simple renommage, donc instantané. Un dossier monté à part (même sur le même volume du NAS) ferait de chaque envoi une copie complète.
   David crée le dossier et l'ajoute comme bibliothèque dans Stash (BL-151) ; Stash peut continuer à indexer d'autres dossiers, Hoard ne s'intéresse qu'à celui-ci.
2. **Réglages serveur** : `stash_url` (vide = fonction coupée), `stash_api_key`, `stash_folder` (chemin relatif dans Hoard, défaut `_stash`), `stash_path_prefix` (le chemin de ce dossier vu par Stash, par exemple `/data/_stash` ; la correspondance se fait par remplacement de préfixe).
   La clé est **en écriture seule** : `/api/settings` ne la renvoie jamais, seulement « clé enregistrée oui/non ». Un bouton « Tester la connexion » affiche la version de Stash ou l'erreur exacte.
3. **Le navigateur ne parle jamais à Stash.** Le backend fait toutes les requêtes GraphQL, et sert les médias de Stash par un proxy `GET /api/stash/scene/{id}/{kind}` (`kind` dans une liste fermée : `screenshot`, `preview`, `webp`, `vtt/thumbs`, `vtt/sprite`, `vtt/chapter`, `funscript`). La clé ne sort pas du serveur. Pour HereSphere et FPX, ces URL portent le jeton signé existant (même mécanisme que `/api/file`).
4. **« Envoyer à Stash »** (menu contextuel d'une vidéo, et sélection multiple) :
   1. déplacer le fichier dans `stash_folder` par le mécanisme de déplacement existant (job, collision, migration de `progress`) ;
   2. `metadataScan` sur le seul chemin déplacé, puis attendre le job (`findJob`) ;
   3. retrouver la scène par son chemin ;
   4. recopier la position (`sceneSaveActivity`) et, si la vidéo est vue, une lecture (`sceneAddPlay`) ;
   5. si Stash a une source d'identification configurée, proposer « Identifier automatiquement » (`metadataIdentify` sur cette scène). Sans source, l'option n'apparaît pas — c'est le cas de David aujourd'hui.
   L'état de l'envoi se voit dans la file des jobs existante. Si Stash est injoignable après le déplacement, le fichier reste dans le dossier, l'erreur le dit, et le scan normal de Stash le rattrapera.
   Les tags de Hoard ne sont **pas** envoyés (David ne s'en sert pas).
5. **La progression reste dans Hoard**, qui la recopie dans Stash pour les vidéos du dossier : position à chaque écriture dans `progress` (limitée à une requête toutes les 30 s par vidéo, plus pause et fermeture), `sceneAddPlay` au passage « vu ». Toutes les voies de lecture passent par là : lecteur web, suivi FPX, événements HereSphere. Pas de synchro de Stash vers Hoard dans ce lot : David ne lit pas dans Stash.
6. **Infos de Stash dans Hoard**, pour les seules vidéos du dossier :
   - liste : vignette de Stash, note, studio et performers en ligne secondaire ; une seule requête `findScenes` par dossier affiché, mise en cache quelques minutes ;
   - lecteur web : vignettes au survol de la barre de lecture (`vtt/thumbs`), markers en chapitres sur la barre ;
   - HereSphere : `thumbnailImage`, `thumbnailVideo`, tags préfixés selon l'usage HereSphere (`Performer:`, `Studio:`, `Tag:`), markers en tags horodatés, note, et `scripts` quand la scène a un funscript.
7. **Dans le dossier de Stash, déplacer et supprimer passent par Stash** : `moveFiles` pour un déplacement ou un renommage qui reste dans le dossier, `sceneDestroy(delete_file: true, delete_generated: true)` pour une suppression. Un déplacement qui **sort** du dossier se fait par le disque comme aujourd'hui, puis Hoard demande à Stash de retirer la scène sans toucher au fichier (`sceneDestroy` sans `delete_file`). Stash injoignable : refus clair, rien ne bouge.
8. **Sécurité** : la clé n'est envoyée qu'à `stash_url` ; le proxy refuse tout `kind` hors liste et tout id non numérique ; les nouvelles routes sont derrière l'authentification habituelle.

## Hors périmètre

- Vue de la collection par tag, performer ou studio (plus tard, si l'usage le demande).
- Détection des doublons avant envoi (empreinte phash de Stash).
- Synchro de la progression de Stash vers Hoard.
- Écrire dans Stash autre chose que la progression et ce qui est décrit ici (tags, note, performers se gèrent dans Stash).

## Tickets

| # | Ticket | Status |
|---|--------|--------|
| 01 | [BL-147 — Se connecter à Stash](tickets/01-connection.md) | ⬜ |
| 02 | [BL-148 — Envoyer une vidéo à Stash](tickets/02-send.md) | ⬜ |
| 03 | [BL-149 — Les infos de Stash dans Hoard, la progression dans Stash](tickets/03-show-and-sync.md) | ⬜ |
| 04 | [BL-150 — Déplacer et supprimer dans le dossier de Stash](tickets/04-file-ops.md) | ⬜ |
| 05 | [BL-151 — Préparer Stash et essayer (David)](tickets/05-setup-and-trial.md) | 🧑 |

Une seule branche et une seule PR pour BL-147 à BL-150.
