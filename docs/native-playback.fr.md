# Hoard - Investigation sur la lecture native

## Objectif

BL-019 est un ticket de recherche. L'objectif est de décider quand Hoard doit conserver le chemin de lecture native du navigateur et quand il doit basculer vers `/api/transcode`, en particulier sur iPad et sur les autres clients basés sur Safari.

Ce document reste volontairement pragmatique : il ne cherche pas à lister tous les profils de codecs publiés par tous les navigateurs. Il identifie les combinaisons que Hoard peut traiter comme sûres, celles qui exigent une vérification, et celles qui doivent rester sur un chemin de repli.

## Comportement actuel de Hoard

Aujourd'hui, Hoard suit ce flux :

1. Récupérer `/api/media-info` à la demande pour le fichier sélectionné.
2. Construire des chaînes MIME tenant compte des codecs à partir des métadonnées ffprobe.
3. Utiliser `video.canPlayType()` comme premier filtre.
4. Quand il est disponible, utiliser `navigator.mediaCapabilities.decodingInfo()` avec les métadonnées exactes du fichier.
5. Ouvrir le fichier via `/api/stream` uniquement quand le support est confirmé ou reste plausible.
6. Si le probing rejette la lecture native, ou si le navigateur échoue ensuite avec `MEDIA_ERR_SRC_NOT_SUPPORTED`, retenter via `/api/transcode`.

Cela conserve `/api/transcode` comme échappatoire de compatibilité, tout en déplaçant la majorité des décisions plus tôt pour éviter d'attendre systématiquement un échec de chargement natif avant de basculer.

## Matrice de compatibilite

Le conteneur et le codec doivent être évalués ensemble. Un codec peut être pris en charge dans un conteneur et échouer dans un autre.

| Combinaison | Recommandation Hoard | Pourquoi |
|---|---|---|
| MP4 + vidéo H.264/AVC + audio AAC | Préférer nativement par défaut | C'est la base la plus compatible entre navigateurs. Apple recommande explicitement le MP4 encodé en H.264 pour les fichiers statiques, et MDN traite toujours MP4/H.264 comme le fallback le plus large. |
| MP4 + vidéo HEVC/H.265 + audio AAC | Vérifier d'abord, ne jamais supposer | Safari et Safari iOS prennent largement en charge HEVC sur le matériel Apple compatible, mais hors Safari le support dépend de l'OS, du navigateur, d'extensions et du décodage matériel. Ce n'est pas une base web universelle. |
| MP4 + vidéo AV1 + audio AAC ou Opus | Vérifier d'abord, ne jamais supposer | AV1 est largement disponible dans Chromium et Firefox, mais le support Safari reste limité au matériel récent équipé d'un décodeur adapté. |
| WebM + vidéo VP8/VP9 + audio Opus/Vorbis | Vérifier d'abord, mais le natif est raisonnable sur navigateurs modernes | WebM est maintenant largement disponible, y compris sur Safari récent, mais les anciennes versions Safari et iOS ont longtemps été partielles. Hoard doit le traiter comme moderne-natif, pas universel-natif. |
| MKV / Matroska avec codecs web à l'intérieur | Ne pas préférer nativement par défaut | Le support HTML5 navigateur n'est pas défini de façon fiable par le seul conteneur, et Matroska reste un mauvais pari par défaut pour la lecture directe dans le navigateur. |
| MOV / QuickTime historique / conteneurs MPEG anciens | Ne pas préférer nativement par défaut | Les conteneurs historiques ou très dépendants d'une plate-forme ne constituent pas une base web solide, même quand le codec embarqué est courant. |

## Conclusions pratiques pour Hoard

### Base sûre en lecture native

Si Hoard sait qu'un fichier est en `video/mp4` avec vidéo H.264/AVC et audio AAC, la lecture native peut rester le choix par défaut.

### Formats qui doivent être vérifiés selon l'appareil

Ces formats ne doivent être préférés nativement qu'après vérification du navigateur et de l'appareil courants :

- HEVC / H.265
- AV1
- WebM / VP8 / VP9
- Tout ce qui dépend du support Safari récent
- Toute combinaison avec piste audio atypique, profondeur de couleur élevée, HDR ou particularité de conteneur

### Formats qui doivent rester sur des chemins de repli

Ces formats ne doivent pas être traités comme sûrs côté navigateur tant que Hoard ne dispose pas d'une preuve contraire :

- MKV / Matroska
- MOV et autres conteneurs historiques
- Combinaisons conteneur / codec non identifiées

## Stratégie de détection implémentée

1. `/api/media-info` retourne les métadonnées d'un fichier sélectionné via ffprobe.
2. Le frontend construit à partir de cette réponse des chaînes MIME tenant compte des codecs.
3. `video.canPlayType(contentType)` écarte tôt les combinaisons manifestement non supportées.
4. `navigator.mediaCapabilities.decodingInfo()` est utilisé quand le navigateur le supporte et que les métadonnées sont assez complètes.
5. La lecture native reste le choix par défaut seulement pour la base sûre ou pour les formats que le probing navigateur ne rejette pas.
6. `/api/transcode` reste le fallback quand le probing rejette la lecture native ou quand le chargement natif échoue malgré tout à l'exécution.

## Limites restantes

- Hoard ne met pas encore en cache les résultats de probing entre les sessions.
- La logique de fallback reste limitée au player ; la liste de fichiers n'affiche pas encore d'indication de compatibilité codec.
- Les fichiers inconnus ou décrits partiellement reposent encore sur un `/api/stream` optimiste puis un fallback à l'exécution.

## Règles à conserver

- Ne pas décider à partir du seul user agent.
- Ne pas assimiler "iPad" à "tous les fichiers HEVC passent en natif".
- Ne pas assimiler "Safari supporte WebM" à "toutes les combinaisons WebM sont sûres".
- Traiter le conteneur, les codecs et la capacité matérielle comme des entrées distinctes.
- Conserver `/api/transcode` comme échappatoire de compatibilité même après ajout du probing.

## Règle produit actuelle

Hoard suit désormais ces règles :

1. MP4/H.264/AAC reste universellement native-first.
2. Les familles HEVC, AV1 et WebM ne restent natives que si le probing navigateur ne les rejette pas.
3. MKV et les conteneurs historiques restent prudents et finissent généralement sur des chemins de fallback, sauf si le navigateur les accepte clairement.
4. `/api/transcode` reste obligatoire comme dernier filet de compatibilité.

## Sources utilisées

- Documentation Apple WebKit sur la livraison de contenu vidéo dans Safari, y compris la recommandation d'utiliser du MP4 H.264 pour les fichiers statiques.
- Documentation MDN pour `HTMLMediaElement.canPlayType()`.
- Documentation MDN pour `MediaCapabilities.decodingInfo()`.
- Guides MDN sur les conteneurs média, la compatibilité codec et la gestion des médias non supportés.
- Tableaux Can I Use pour HEVC, WebM et AV1, consultés le 2026-04-12 pour valider les tendances.
