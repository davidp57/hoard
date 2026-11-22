# BL-152 — Tags et note de Stash gérés depuis Hoard

Status: ⬜ ready
Lot: [FEAT-STASH](../PRD.md)

## Pourquoi

David, 2026-11-22, pendant l'essai : « Ça serait bien d'avoir les tags de Stash qui soient gérés par Hoard. Comme ça, on pourrait tranquillement les sélectionner dans Hoard. »
Il ne se sert pas des tags de Hoard (`file_tags`), restés enfermés dans Hoard.
Hoard a déjà tout l'outillage : la fenêtre Tags (`openTagModal`, étiquettes, saisie avec suggestions) et la barre de filtre par tag de la liste (`_renderTagFilterBar`).

## Quoi (décisions validées par David le 2026-11-22)

Pour les seules vidéos de `stash_folder` ; ailleurs, rien ne change.

1. **La fenêtre Tags lit et écrit les tags de la scène Stash** (`sceneUpdate` avec `tag_ids`). Même point d'entrée qu'aujourd'hui : menu contextuel et menu du lecteur, manette comprise.
2. **Suggestions = tags existants de Stash** (`findTags`), les plus utilisés en premier (nombre de scènes), filtrés par la saisie. Un tag absent est **créé** dans Stash (`tagCreate`). La casse de Stash est gardée : pas de passage en minuscules pour ces tags.
3. **Barre de filtre par tag** : dans `stash_folder`, elle porte les tags de Stash et filtre la liste sur eux.
4. **Note** : des étoiles (1 à 5) dans le menu de la vidéo (contextuel et lecteur), écrites dans Stash (`sceneUpdate` avec `rating100`, 1 étoile = 20) ; une action pour l'effacer. La note affichée dans la liste (BL-149) se met à jour aussitôt.
5. Performers et studio restent gérés dans Stash : hors périmètre.

## Critères d'acceptation

- [ ] Fenêtre Tags sur une vidéo de `stash_folder` : affiche les tags Stash de la scène ; ajouter et retirer écrivent dans Stash ; la liste et la barre de filtre se mettent à jour sans attendre la fin du cache de BL-149.
- [ ] Suggestions triées par usage, filtrées par la saisie, casse de Stash conservée ; un tag nouveau est créé une seule fois (pas de doublon si un tag de même nom existe, comparaison insensible à la casse).
- [ ] Barre de filtre : dans `stash_folder`, filtre sur les tags de Stash ; ailleurs, comportement actuel.
- [ ] Note en étoiles dans le menu contextuel et le menu du lecteur, atteignable à la manette ; effacer possible ; liste rafraîchie.
- [ ] Vidéo de `stash_folder` sans scène Stash (pas encore scannée) : la fenêtre le dit clairement, rien n'est écrit dans `file_tags`.
- [ ] Stash injoignable : erreur claire, rien n'est écrit nulle part.
- [ ] Hors de `stash_folder`, ou sans Stash réglé : tags Hoard et barre de filtre inchangés.
- [ ] Tests pytest avec le faux Stash : lecture, ajout, retrait, création de tag (et pas de doublon), note, scène absente, Stash injoignable.
- [ ] Doc : guide utilisateur FR + EN (section Stash) ; doc développeur ; changelogs.
