# Hoard - Investigation sur la lecture native

## Objectif

BL-019 est un ticket de recherche. L'objectif est de décider quand Hoard doit conserver le chemin de lecture native du navigateur et quand il doit basculer vers `/api/transcode`, en particulier sur iPad et sur les autres clients basés sur Safari.

Ce document reste volontairement pragmatique : il ne cherche pas à lister tous les profils de codecs publiés par tous les navigateurs. Il identifie les combinaisons que Hoard peut traiter comme sûres, celles qui exigent une vérification, et celles qui doivent rester sur un chemin de repli.

## Comportement actuel de Hoard

Aujourd'hui, Hoard suit ce flux :

1. Ouvrir le fichier via `/api/stream`.
2. Laisser le navigateur tenter la lecture du fichier original avec l'élément HTML5 `<video>`.
3. Si la lecture échoue avec `MEDIA_ERR_SRC_NOT_SUPPORTED`, retenter via `/api/transcode`.

Cette approche reste simple et fonctionne déjà, mais la décision arrive trop tard. L'erreur navigateur n'apparaît qu'après une tentative de chargement, et Hoard ne possède aucune connaissance structurée du conteneur, des codecs, de la profondeur de couleur ou des autres contraintes du fichier.

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

## Stratégie de détection recommandée

BL-019 n'implémente pas encore cette stratégie, mais fixe la direction recommandée.

1. Ajouter un endpoint de métadonnées léger basé sur `ffprobe`.
2. Retourner au minimum : conteneur, codec vidéo, codec audio, largeur, hauteur, débit, fréquence d'image, canaux audio, fréquence d'échantillonnage et profondeur de couleur quand elle est disponible.
3. Construire côté frontend une chaîne MIME précise, par exemple `video/mp4; codecs="avc1.640028, mp4a.40.2"`.
4. Appeler `video.canPlayType(contentType)` comme premier filtre peu coûteux.
5. Quand les métadonnées sont complètes et que `navigator.mediaCapabilities.decodingInfo` est disponible, vérifier exactement le fichier en `type: "file"`.
6. Utiliser la lecture native uniquement lorsque le navigateur annonce un support effectif.
7. Conserver le retry actuel sur `/api/transcode` via `video.onerror` comme filet de sécurité final.
8. Mettre en cache les résultats de vérification par empreinte média et signature navigateur afin d'éviter de recalculer la décision à chaque ouverture.

## Règles à conserver

- Ne pas décider à partir du seul user agent.
- Ne pas assimiler "iPad" à "tous les fichiers HEVC passent en natif".
- Ne pas assimiler "Safari supporte WebM" à "toutes les combinaisons WebM sont sûres".
- Traiter le conteneur, les codecs et la capacité matérielle comme des entrées distinctes.
- Conserver `/api/transcode` comme échappatoire de compatibilité même après ajout du probing.

## Décision produit à l'issue de cette investigation

La conclusion immédiate pour Hoard doit être :

1. Conserver le fallback actuel `/api/stream` puis `/api/transcode` tant que le support de métadonnées n'existe pas.
2. Planifier l'extraction de métadonnées avant de changer les heuristiques native-versus-transcode.
3. Une fois le probing ajouté, ne marquer comme universellement native-first que MP4/H.264/AAC.
4. Marquer les familles HEVC, AV1 et WebM comme lecture native conditionnelle sur vérification à l'exécution.
5. Conserver des règles prudentes de fallback pour MKV et les conteneurs historiques.

## Sources utilisées

- Documentation Apple WebKit sur la livraison de contenu vidéo dans Safari, y compris la recommandation d'utiliser du MP4 H.264 pour les fichiers statiques.
- Documentation MDN pour `HTMLMediaElement.canPlayType()`.
- Documentation MDN pour `MediaCapabilities.decodingInfo()`.
- Guides MDN sur les conteneurs média, la compatibilité codec et la gestion des médias non supportés.
- Tableaux Can I Use pour HEVC, WebM et AV1, consultés le 2026-04-12 pour valider les tendances.
