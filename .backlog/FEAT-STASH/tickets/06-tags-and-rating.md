# BL-152 — Tags et note de Stash gérés depuis Hoard

Status: ✅ done
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

## Ajout du 2026-11-22 (validé par David)

À l'essai de la v2.9.6, une vidéo bien identifiée par la stash-box n'affichait dans la liste que la vignette de Stash : ni titre, ni studio, ni performers.

6. **Titre** : dans `stash_folder`, une scène qui a un titre est listée sous ce titre, le nom de fichier en petit dessous. Le tri par nom suit le titre affiché ; la recherche porte toujours sur les noms de fichiers (le nom reste visible sous le titre). Sans titre, rien ne change.
7. **Relecture après identification** : cause confirmée dans le code. Hoard lançait `metadataIdentify` sans attendre son job ni vider le cache ; une lecture de la liste entre la fin du scan et la fin de l'identification gardait 3 min une fiche sans titre, studio ni performers. Hoard attend maintenant le job d'identification, puis vide le cache des scènes.

## Critères d'acceptation

- [x] Fenêtre Tags sur une vidéo de `stash_folder` : affiche les tags Stash de la scène ; ajouter et retirer écrivent dans Stash ; la liste et la barre de filtre se mettent à jour sans attendre la fin du cache de BL-149.
- [x] Suggestions triées par usage, filtrées par la saisie, casse de Stash conservée ; un tag nouveau est créé une seule fois (pas de doublon si un tag de même nom existe, comparaison insensible à la casse).
- [x] Barre de filtre : dans `stash_folder`, filtre sur les tags de Stash ; ailleurs, comportement actuel.
- [x] Note en étoiles dans le menu contextuel et le menu du lecteur, atteignable à la manette ; effacer possible ; liste rafraîchie.
- [x] Vidéo de `stash_folder` sans scène Stash (pas encore scannée) : la fenêtre le dit clairement, rien n'est écrit dans `file_tags`.
- [x] Stash injoignable : erreur claire, rien n'est écrit nulle part.
- [x] Hors de `stash_folder`, ou sans Stash réglé : tags Hoard et barre de filtre inchangés.
- [x] Tests pytest avec le faux Stash : lecture, ajout, retrait, création de tag (et pas de doublon), note, scène absente, Stash injoignable.
- [x] Titre de Stash à la place du nom de fichier dans la liste de `stash_folder`, nom de fichier dessous ; tri par nom sur le titre affiché ; sans titre, rien ne change.
- [x] Après l'identification, la liste relit la fiche : titre, studio et performers trouvés par l'identification s'affichent (test contre le faux Stash qui reproduit une lecture pendant l'identification).
- [x] Doc : guide utilisateur FR + EN (section Stash) ; doc développeur ; changelogs.
