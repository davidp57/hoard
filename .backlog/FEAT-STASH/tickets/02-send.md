# BL-148 — Envoyer une vidéo à Stash

Status: ⬜ ready
Lot: [FEAT-STASH](../PRD.md)

## Quoi

Décision 4 du PRD : l'action « Envoyer à Stash ».

## Critères d'acceptation

- [ ] « Envoyer à Stash » dans le menu contextuel d'une vidéo et pour une sélection multiple ; absent si Stash n'est pas réglé, ou pour un fichier déjà dans `stash_folder` ; atteignable à la manette.
- [ ] Déplacement par le mécanisme existant (job, collision « remplacer / annuler », migration de `progress`).
- [ ] `metadataScan` sur le seul chemin déplacé, attente du job par `findJob`, scène retrouvée par son chemin.
- [ ] Position recopiée (`sceneSaveActivity`) ; une lecture ajoutée (`sceneAddPlay`) si la vidéo est vue.
- [ ] Option « Identifier automatiquement » (`metadataIdentify` sur la scène) proposée seulement si Stash a une source d'identification configurée.
- [ ] Avancement et erreurs visibles dans la file des jobs ; Stash injoignable après le déplacement : le fichier reste dans le dossier et l'erreur le dit.
- [ ] Tests pytest avec le faux Stash : envoi complet, scan qui échoue, scène introuvable, Stash injoignable, identification avec et sans source.
- [ ] Doc : guide utilisateur FR + EN ; doc développeur.
