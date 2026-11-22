# BL-153 — Garder pour éditer : tags « Identify » et « Edit », coupe qui hérite de sa source

Status: ⬜ ready
Lot: [FEAT-STASH](../PRD.md)
Dépend de : BL-152 (tags de Stash et barre de filtre dans Hoard)

## Pourquoi

David, 2026-11-22 : il édite souvent une vidéo avant de la garder (il découpe pour ne garder que ce qui l'intéresse).
Une coupe n'a plus l'empreinte de la vidéo d'origine : Stash ne peut pas l'identifier.
Et s'il range la vidéo entière dans `[[_keep` sans marque, il ne sait plus qu'elle est à éditer.

Solution retenue (option B de la discussion) : la vidéo **entière** entre dans Stash, où elle est identifiée ; deux tags indépendants disent si elle est identifiée et si elle est à éditer ; la coupe faite dans Hoard **hérite de la fiche** de sa source.
`[[_edit` n'est plus utile pour ce circuit.

| Tags Stash | Sens |
|---|---|
| Identify | Gardée, identification pas encore validée |
| Identify + Edit | À éditer, identification pas encore validée |
| Edit | Identification validée, prête à éditer |
| aucun | Gardée, identifiée, terminée |

## Décisions (validées par David le 2026-11-22)

1. **Garder** : tout ce qui arrive dans `stash_folder` par Hoard (BL-148) reçoit le tag « Identify ».
2. **Garder pour éditer** : une entrée « Garder pour éditer » dans la liste des dossiers rapides (même geste en deux taps, manette comprise, sélection multiple comprise). Elle déplace vers `stash_folder` et pose « Identify » et « Edit ».
3. **« Identify » n'est jamais retiré par Hoard**, même quand l'identification automatique réussit. David le retire lui-même dans Stash après avoir vérifié la fiche : une identification automatique peut se tromper, et la liste « Identify » de Stash est sa file de vérification.
4. **Filtre « ✂ À éditer »** dans `stash_folder` : n'affiche que les vidéos taguées « Edit ». Une case « Masquer les non identifiées » cache celles qui ont encore « Identify » ; **cochée par défaut**.
5. **La coupe hérite de sa source.** Quand ✂ ou « Exporter les segments » écrit dans `stash_folder` une vidéo coupée d'une vidéo qui a une scène Stash, la nouvelle scène reçoit de la source : titre, date, studio, performers, tags, URL, détails, note. Sans le tag « Edit » ; avec « Identify » si la source l'avait encore. En export individuel, chaque segment hérite de la même façon.
6. **`stash_ids` n'est pas recopié** sur la coupe : si David envoie un jour ses empreintes à la stash-box, celles de la coupe partiraient comme si c'était la scène entière.
7. **Originale non gardée** (« garder l'original » décoché) : Hoard la supprime par Stash (`sceneDestroy` avec `delete_file` et `delete_generated`), comme une suppression dans `stash_folder` (BL-150).
8. **Noms réglables** dans *Paramètres › Stash* : « Identify » et « Edit » par défaut. Hoard crée ces tags dans Stash s'ils n'existent pas.
9. Les 194 vidéos de `[[_edit` restent où elles sont : David les fera passer par « Garder pour éditer » au fil de l'eau ou par sélection multiple.

## Critères d'acceptation

- [ ] Arrivée dans `stash_folder` : tag « Identify » posé sur la scène, une fois le scan fini.
- [ ] « Garder pour éditer » dans la liste des dossiers rapides (menu, manette, sélection multiple) : déplace et pose « Identify » + « Edit ».
- [ ] Aucun chemin de code ne retire « Identify » (identification automatique comprise).
- [ ] Filtre « ✂ À éditer » dans `stash_folder`, case « Masquer les non identifiées » cochée par défaut ; absent ailleurs.
- [ ] Coupe ✂ et export des segments (fusionné et individuel) vers `stash_folder` depuis une vidéo qui a une scène : la nouvelle scène hérite des champs de la décision 5, sans « Edit », avec « Identify » si la source l'avait, sans `stash_ids`.
- [ ] Source sans scène Stash : la coupe est déclarée comme une arrivée normale (« Identify » seul).
- [ ] Originale non gardée : supprimée par Stash ; Stash injoignable : la coupe reste, l'originale aussi, erreur claire dans le job.
- [ ] Réglages des deux noms de tags ; tags créés s'ils manquent, sans doublon (comparaison insensible à la casse).
- [ ] Tests pytest avec le faux Stash pour chaque cas ci-dessus.
- [ ] Doc : guide FR + EN (le circuit garder / garder pour éditer / identifier / éditer, le tableau des tags) ; doc développeur ; changelogs.
