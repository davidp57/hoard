# Lot FEAT-STASH — Hoard trie et lit, Stash garde et décrit

Status: 🧑 waiting-human

## Problem Statement

David a installé Stash sur le NAS (2026-11-22).
Il garde Hoard pour regarder ses vidéos, et veut que Stash gère les vidéos qu'il garde.
Il veut que les vidéos gardées arrivent dans Stash avec ce que Hoard sait d'elles, et retrouver dans Hoard ce que Stash sait de ces vidéos.

## Le circuit de David (2026-11-22)

Les téléchargements arrivent dans `downloads`, ou dans un de ses sous-dossiers.
David les regarde dans Hoard et tranche avec les dossiers rapides :

| Décision | Geste dans Hoard | Destination |
|---|---|---|
| Pas bien | Supprimer | — |
| Bien, on garde | Dossier rapide | `downloads/[[_keep` |
| Bien, mais à éditer | Dossier rapide | `downloads/[[_edit` |
| Pas sûr | Dossier rapide | `downloads/[[_review` |
| Édition faite | ✂, « Exporter les segments », ou un autre logiciel | `[[_keep`, a priori |

Les trois dossiers sont des sous-dossiers de `downloads`, donc **visibles dans Hoard**.
Relevé le 2026-11-22 : `[[_keep` 40 vidéos (17 Go), `[[_edit` 194, `[[_review` 1 064.

## Ce qui est établi (2026-11-22)

- **Stash v0.32.0** (sortie le 2026-11-02), API GraphQL sur `/graphql`.
- **Instance de David** : `127.0.0.1:9999` sur le NAS, identifiants activés (`/` renvoie vers `/login`, `/graphql` répond 401 sans clé). Version installée et bibliothèques configurées non lues faute de clé ; le premier scan est en cours.
- **Clé d'API** : en-tête `ApiKey` ou paramètre `?apikey=` (`internal/api/authentication.go`). Elle se crée dans Stash, *Settings → Security*.
- **Schéma** (`graphql/schema/schema.graphql`, `types/scene.graphql`, `types/metadata.graphql`) :
  - lecture : `findScenes` (filtre par chemin), `findScene`, `findJob` ;
  - scène : `resume_time`, `play_count`, `play_duration`, `last_played_at`, `o_counter`, `rating100`, `organized`, `tags`, `performers`, `studio`, `scene_markers`, `interactive`, `files`, `paths` ;
  - écriture : `metadataScan(input: {paths})` scanne des chemins précis et rend un id de job ; `metadataIdentify(input: {sources, sceneIDs})` identifie des scènes précises ; `sceneUpdate` ; `sceneSaveActivity(id, resume_time, playDuration)` ; `sceneAddPlay(id)` ; `moveFiles` ; `deleteFiles` ; `sceneDestroy(delete_file, delete_generated)`.
- **Médias générés**, sous `/scene/{id}/` : `screenshot`, `preview` (mp4), `webp`, `vtt/thumbs` + `vtt/sprite` (vignettes de la barre de lecture), `vtt/chapter` (markers), `funscript`, `interactive_heatmap`, `caption`.
- **Pas d'API HereSphere ni DeoVR dans le cœur de Stash** (rien dans `internal/api`). Hoard sert déjà HereSphere (FEAT-HERESPHERE), mais envoie aujourd'hui `tags: []`, ni vignette ni script.
- **Réponses de David** : aucune source d'identification (stash-box, scrapers) n'est configurée, il attend la fin du premier scan ; il n'utilise pas les tags de Hoard (`file_tags`).
- **Le nom du dossier commence par `[[`.** `[` est un caractère spécial dans une expression régulière et dans un motif de fichiers : tout filtre de chemin envoyé à Stash (ou glob côté Hoard) doit l'échapper.

## Solution

Hoard se connecte à Stash par son API, avec une clé gardée côté serveur.
**Tout fichier qui arrive dans `[[_keep` par Hoard est déclaré à Stash**, quel que soit le geste : dossier rapide, « Déplacer », renommage, ✂ ou export des segments. Hoard fait scanner ce fichier, puis recopie « vu » et la position de reprise. Il n'y a pas d'action « Envoyer à Stash » à part : David continue de trier avec ses dossiers rapides.
Pour les vidéos de `[[_keep`, Hoard affiche ce que Stash sait (vignette, performers, studio, tags, note, markers) dans la liste, dans le lecteur et dans HereSphere, et recopie la progression dans Stash.
Dans `[[_keep`, déplacer et supprimer passent par Stash, pour que Stash ne perde pas ses métadonnées.
`[[_edit`, `[[_review` et le reste de `downloads` ne concernent pas Stash. Sans réglage Stash, Hoard marche exactement comme aujourd'hui.

## Décisions (Claude, 2026-11-22 — valent par défaut)

1. **Le dossier de Stash est `[[_keep`**, sous la racine de Hoard. Un déplacement dans un même montage Docker est un renommage, donc instantané. Stash ne doit indexer que ce dossier (BL-151) : s'il indexait tout `downloads`, il décrirait aussi les vidéos pas encore triées.
2. **Réglages serveur** : `stash_url` (vide = fonction coupée), `stash_api_key`, `stash_folder` (chemin relatif dans Hoard, défaut `[[_keep`), `stash_path_prefix` (le chemin de ce dossier vu par Stash ; la correspondance se fait par remplacement de préfixe), `stash_identify` (identifier à l'arrivée, coupé par défaut).
   La clé est **en écriture seule** : `/api/settings` ne la renvoie jamais, seulement « clé enregistrée oui/non ». Un bouton « Tester la connexion » affiche la version de Stash ou l'erreur exacte.
3. **Le navigateur ne parle jamais à Stash.** Le backend fait toutes les requêtes GraphQL, et sert les médias de Stash par un proxy `GET /api/stash/scene/{id}/{kind}` (`kind` dans une liste fermée : `screenshot`, `preview`, `webp`, `vtt/thumbs`, `vtt/sprite`, `vtt/chapter`, `funscript`). La clé ne sort pas du serveur. Pour HereSphere et FPX, ces URL portent le jeton signé existant (même mécanisme que `/api/file`).
4. **Arrivée dans `[[_keep`.** À la fin de tout job de Hoard qui écrit une vidéo dans `stash_folder` (déplacement, renommage, découpe ✂, export des segments) :
   1. `metadataScan` sur les seuls chemins arrivés, puis attente du job (`findJob`) ;
   2. scène retrouvée par son chemin ;
   3. position recopiée (`sceneSaveActivity`) et, si la vidéo est vue, une lecture (`sceneAddPlay`) ;
   4. si `stash_identify` est actif et que Stash a une source d'identification, `metadataIdentify` sur ces scènes. Le réglage reste caché tant que Stash n'a pas de source — c'est le cas de David aujourd'hui.
   Le geste de David ne change pas et ne ralentit pas : la déclaration à Stash tourne après le déplacement, en tâche de fond. Si Stash est injoignable, le fichier reste dans `[[_keep`, l'échec est écrit dans le journal (`WARNING stash:`), et le scan normal de Stash le rattrapera.
   Un fichier posé dans `[[_keep` par un autre logiciel n'est pas vu par Hoard : le scan normal de Stash le prend.
   Les tags de Hoard ne sont **pas** envoyés (David ne s'en sert pas).
5. **La progression reste dans Hoard**, qui la recopie dans Stash pour les vidéos de `[[_keep` : position à chaque écriture dans `progress` (limitée à une requête toutes les 30 s par vidéo, plus pause et fermeture), `sceneAddPlay` au passage « vu ». Toutes les voies de lecture passent par là : lecteur web, suivi FPX, événements HereSphere. Pas de synchro de Stash vers Hoard dans ce lot : David ne lit pas dans Stash.
6. **Infos de Stash dans Hoard**, pour les seules vidéos de `[[_keep` :
   - liste : vignette de Stash, note, studio et performers en ligne secondaire ; une seule requête `findScenes` par dossier affiché, mise en cache quelques minutes ;
   - lecteur web : vignettes au survol de la barre de lecture (`vtt/thumbs`), markers en chapitres sur la barre ;
   - HereSphere : `thumbnailImage`, `thumbnailVideo`, tags préfixés selon l'usage HereSphere (`Performer:`, `Studio:`, `Tag:`), markers en tags horodatés, note, et `scripts` quand la scène a un funscript.
7. **Dans `[[_keep`, déplacer et supprimer passent par Stash** : `moveFiles` pour un déplacement ou un renommage qui reste dans le dossier, `sceneDestroy(delete_file: true, delete_generated: true)` pour une suppression. Un déplacement qui **sort** du dossier (vers `[[_edit`, par exemple) se fait par le disque comme aujourd'hui, puis Hoard demande à Stash de retirer la scène sans toucher au fichier (`sceneDestroy` sans `delete_file`). Stash injoignable : refus clair, rien ne bouge.
8. **Sécurité** : la clé n'est envoyée qu'à `stash_url` ; le proxy refuse tout `kind` hors liste et tout id non numérique ; les nouvelles routes sont derrière l'authentification habituelle.

## Hors périmètre

- Vue de la collection par tag, performer ou studio (plus tard, si l'usage le demande).
- Détection des doublons avant de garder (empreinte phash de Stash).
- Synchro de la progression de Stash vers Hoard.
- Écrire dans Stash autre chose que la progression et ce qui est décrit ici (tags, note, performers se gèrent dans Stash).
- Les 40 vidéos déjà dans `[[_keep` : le premier scan de Stash les prend ; leur progression Hoard n'est pas recopiée rétroactivement.

## Tickets

| # | Ticket | Status |
|---|--------|--------|
| 01 | [BL-147 — Se connecter à Stash](tickets/01-connection.md) | ✅ |
| 02 | [BL-148 — Déclarer à Stash ce qui arrive dans `[[_keep`](tickets/02-send.md) | ✅ |
| 03 | [BL-149 — Les infos de Stash dans Hoard, la progression dans Stash](tickets/03-show-and-sync.md) | ✅ |
| 04 | [BL-150 — Déplacer et supprimer dans le dossier de Stash](tickets/04-file-ops.md) | ✅ |
| 05 | [BL-151 — Préparer Stash et essayer (David)](tickets/05-setup-and-trial.md) | 🧑 |
| 06 | [BL-152 — Tags et note de Stash gérés depuis Hoard](tickets/06-tags-and-rating.md) | ⬜ |

Une seule branche et une seule PR pour BL-147 à BL-150 (PR #90, v2.9.6). BL-152, demandé pendant l'essai, a sa propre PR.
