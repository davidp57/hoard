# BL-148 — Déclarer à Stash ce qui arrive dans `[[_keep`

Status: ⬜ ready
Lot: [FEAT-STASH](../PRD.md)

## Quoi

Décision 4 du PRD : tout fichier vidéo que Hoard écrit dans `stash_folder` est déclaré à Stash. Pas d'action dédiée : David trie avec ses dossiers rapides.

## Critères d'acceptation

- [ ] Déclenché à la fin de chaque job qui écrit une vidéo dans `stash_folder` : déplacement (dossier rapide ou « Déplacer »), renommage, découpe ✂, export des segments. Un dossier déplacé dans `stash_folder` déclare chaque vidéo qu'il contient.
- [ ] Le geste ne ralentit pas : le déplacement se termine comme aujourd'hui, la déclaration tourne ensuite en tâche de fond.
- [ ] `metadataScan` sur les seuls chemins arrivés, attente du job par `findJob`, scène retrouvée par son chemin (préfixe traduit, `[` échappé dans tout filtre de chemin).
- [ ] Position recopiée (`sceneSaveActivity`) ; une lecture ajoutée (`sceneAddPlay`) si la vidéo est vue.
- [ ] Réglage « Identifier les vidéos à leur arrivée dans Stash » (`stash_identify`), visible seulement si Stash a une source d'identification ; actif : `metadataIdentify` sur les scènes arrivées.
- [ ] Stash injoignable, scan en échec ou scène introuvable : le fichier reste dans `stash_folder`, `WARNING stash:` dans le journal avec chemin et cause, aucune erreur bloquante pour David.
- [ ] Tests pytest avec le faux Stash : arrivée par déplacement, par renommage, par export ; dossier entier ; nom de dossier avec `[[` ; scan qui échoue ; scène introuvable ; Stash injoignable ; identification avec et sans source.
- [ ] Doc : guide utilisateur FR + EN (le circuit garder / éditer / revoir, ce que fait Hoard à l'arrivée dans le dossier de Stash) ; doc développeur.
