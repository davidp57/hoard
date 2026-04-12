# Hoard - Investigation lecture native

## Objectif

BL-019 est un ticket de recherche. L'objectif est de decider quand Hoard doit conserver le chemin de lecture native du navigateur et quand il doit basculer vers `/api/transcode`, en particulier sur iPad et sur les autres clients bases sur Safari.

Ce document reste volontairement pragmatique : il ne cherche pas a lister tous les profils de codecs publies par tous les navigateurs. Il identifie les combinaisons que Hoard peut traiter comme sures, celles qui exigent une verification, et celles qui doivent rester sur un chemin de repli.

## Comportement actuel de Hoard

Aujourd'hui Hoard suit ce flux :

1. Ouvrir le fichier via `/api/stream`.
2. Laisser le navigateur tenter la lecture du fichier original avec l'element HTML5 `<video>`.
3. Si la lecture echoue avec `MEDIA_ERR_SRC_NOT_SUPPORTED`, retenter via `/api/transcode`.

Cette approche reste simple et fonctionne deja, mais la decision arrive trop tard. L'erreur navigateur n'apparait qu'apres une tentative de chargement, et Hoard ne possede aucune connaissance structuree du conteneur, des codecs, de la profondeur de couleur ou des autres contraintes du fichier.

## Matrice de compatibilite

Le conteneur et le codec doivent etre evalues ensemble. Un codec peut etre pris en charge dans un conteneur et echouer dans un autre.

| Combinaison | Recommendation Hoard | Pourquoi |
|---|---|---|
| MP4 + video H.264/AVC + audio AAC | Preferer nativement par defaut | C'est la base la plus compatible entre navigateurs. Apple recommande explicitement le MP4 encode en H.264 pour les fichiers statiques, et MDN traite toujours MP4/H.264 comme le fallback le plus large. |
| MP4 + video HEVC/H.265 + audio AAC | Verifier d'abord, ne jamais supposer | Safari et Safari iOS prennent largement en charge HEVC sur le materiel Apple compatible, mais hors Safari le support depend de l'OS, du navigateur, d'extensions et du decodage materiel. Ce n'est pas une base web universelle. |
| MP4 + video AV1 + audio AAC ou Opus | Verifier d'abord, ne jamais supposer | AV1 est largement disponible dans Chromium et Firefox, mais le support Safari reste limite au materiel recent equipe d'un decodeur adapte. |
| WebM + video VP8/VP9 + audio Opus/Vorbis | Verifier d'abord, mais le natif est raisonnable sur navigateurs modernes | WebM est maintenant largement disponible, y compris sur Safari recent, mais les anciennes versions Safari et iOS ont longtemps ete partielles. Hoard doit le traiter comme moderne-natif, pas universel-natif. |
| MKV / Matroska avec codecs web a l'interieur | Ne pas preferer nativement par defaut | Le support HTML5 navigateur n'est pas defini de facon fiable par le seul conteneur, et Matroska reste un mauvais pari par defaut pour la lecture directe dans le navigateur. |
| MOV / QuickTime historique / conteneurs MPEG anciens | Ne pas preferer nativement par defaut | Les conteneurs historiques ou tres dependants d'une plate-forme ne constituent pas une base web solide, meme quand le codec embarque est courant. |

## Conclusions pratiques pour Hoard

### Base sure en lecture native

Si Hoard sait qu'un fichier est en `video/mp4` avec video H.264/AVC et audio AAC, la lecture native peut rester le choix par defaut.

### Formats qui doivent etre verifies selon l'appareil

Ces formats ne doivent etre preferes nativement qu'apres verification du navigateur et de l'appareil courants :

- HEVC / H.265
- AV1
- WebM / VP8 / VP9
- Tout ce qui depend du support Safari recent
- Toute combinaison avec piste audio atypique, profondeur de couleur elevee, HDR ou particularite de conteneur

### Formats qui doivent rester sur des chemins de repli

Ces formats ne doivent pas etre traites comme surs cote navigateur tant que Hoard ne dispose pas d'une preuve contraire :

- MKV / Matroska
- MOV et autres conteneurs historiques
- Combinaisons conteneur / codec non identifiees

## Strategie de detection recommandee

BL-019 n'implemente pas encore cette strategie, mais fixe la direction recommandee.

1. Ajouter un endpoint de metadonnees leger base sur `ffprobe`.
2. Retourner au minimum : conteneur, codec video, codec audio, largeur, hauteur, debit, frequence d'image, canaux audio, frequence d'echantillonnage et profondeur de couleur quand elle est disponible.
3. Construire cote frontend une chaine MIME precise, par exemple `video/mp4; codecs="avc1.640028, mp4a.40.2"`.
4. Appeler `video.canPlayType(contentType)` comme premier filtre peu couteux.
5. Quand les metadonnees sont completes et que `navigator.mediaCapabilities.decodingInfo` est disponible, verifier exactement le fichier en `type: "file"`.
6. Utiliser la lecture native uniquement lorsque le navigateur annonce un support effectif.
7. Conserver le retry actuel sur `/api/transcode` via `video.onerror` comme filet de securite final.
8. Mettre en cache les resultats de verification par empreinte media et signature navigateur afin d'eviter de recalculer la decision a chaque ouverture.

## Regles a conserver

- Ne pas decider a partir du seul user agent.
- Ne pas assimiler "iPad" a "tous les fichiers HEVC passent en natif".
- Ne pas assimiler "Safari supporte WebM" a "toutes les combinaisons WebM sont sures".
- Traiter le conteneur, les codecs et la capacite materielle comme des entrees distinctes.
- Conserver `/api/transcode` comme echappatoire de compatibilite meme apres ajout du probing.

## Decision produit a l'issue de cette investigation

La conclusion immediate pour Hoard doit etre :

1. Conserver le fallback actuel `/api/stream` puis `/api/transcode` tant que le support de metadonnees n'existe pas.
2. Planifier l'extraction de metadonnees avant de changer les heuristiques native-versus-transcode.
3. Une fois le probing ajoute, ne marquer comme universellement native-first que MP4/H.264/AAC.
4. Marquer les familles HEVC, AV1 et WebM comme lecture native conditionnelle sur verification a l'execution.
5. Conserver des regles prudentes de fallback pour MKV et les conteneurs historiques.

## Sources utilisees

- Documentation Apple WebKit sur la livraison de contenu video dans Safari, y compris la recommandation d'utiliser du MP4 H.264 pour les fichiers statiques.
- Documentation MDN pour `HTMLMediaElement.canPlayType()`.
- Documentation MDN pour `MediaCapabilities.decodingInfo()`.
- Guides MDN sur les conteneurs media, la compatibilite codec et la gestion des medias non supportes.
- Tableaux Can I Use pour HEVC, WebM et AV1, consultes le 2026-04-12 pour valider les tendances.
