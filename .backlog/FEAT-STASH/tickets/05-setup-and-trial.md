# BL-151 — Préparer Stash et essayer (David)

Status: 🧑 waiting-human
Lot: [FEAT-STASH](../PRD.md)

## Quoi

Ce que seul David peut faire sur le NAS et dans Stash, puis l'essai du lot.

## Étapes

- [ ] Vérifier que le conteneur Stash voit `downloads/[[_keep`, et noter le chemin sous lequel il le voit (valeur de `stash_path_prefix`).
- [ ] Dans Stash (*Settings → Library*), n'indexer que `[[_keep` : pas tout `downloads`, sinon Stash décrit aussi les vidéos pas encore triées (`[[_review`, `[[_edit`, arrivées).
- [ ] Créer une clé d'API dans Stash (*Settings → Security*) et la coller dans les réglages de Hoard.
- [ ] Plus tard, après le premier scan : configurer une source d'identification (stash-box ou scrapers) pour activer « Identifier les vidéos à leur arrivée dans Stash ».
- [ ] Essai : garder une vidéo en cours de lecture par le dossier rapide, vérifier qu'elle apparaît dans Stash avec sa position ; exporter des segments de `[[_edit` vers `[[_keep` ; relire une vidéo gardée dans Hoard et dans FPX ; en renvoyer une vers `[[_edit`, en supprimer une depuis Hoard.
