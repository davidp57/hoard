# BL-154 — « À éditer » et « À identifier » : deux tags spéciaux gérés par Hoard

Status: ✅ done
Lot: [FEAT-STASH](../PRD.md)

## Pourquoi

David, 2026-11-22, à l'essai de la v2.9.8 : la barre de filtre de `[[_keep` montre le tag Stash « Edit » et, à côté, le filtre « ✂ À éditer » qui a l'air d'un tag ; il les a pris pour deux tags, et « ✂ À éditer » semblait ne pas marcher (sa vidéo avait encore « Identify », masquée par défaut).
Sa décision : « Garde le tag à éditer et enlève le tag Edit. Les deux tags à éditer et à identifier, ce sont deux tags spéciaux que Hoard gère. Et tous les autres tags doivent être après : ce sont les tags qui sont vraiment sur les vidéos de Stash. »

## Décisions (David, 2026-11-22 ; points 3 et 4 : recos de Claude annoncées à David)

1. **Barre de filtre dans `stash_folder`** : d'abord les deux tags spéciaux, « ✂ À éditer » puis « 🔍 À identifier », avec un style qui les distingue des tags ordinaires ; ensuite les vrais tags de Stash.
2. **Les tags techniques n'apparaissent plus comme des tags** : `stash_tag_edit` (« Edit ») et `stash_tag_identify` (« Identify ») sont retirés de la liste des tags ordinaires, partout dans Hoard (barre de filtre, fenêtre 🏷, suggestions, ligne de la liste si les tags y sont montrés). Ils restent les vrais tags dans Stash.
3. **« ✂ À éditer »** garde son comportement de BL-153 : vidéos taguées « Edit », avec la case « Masquer les non identifiées » cochée par défaut. **« 🔍 À identifier »** montre les vidéos taguées « Identify ».
4. **Fenêtre 🏷** d'une vidéo de `stash_folder` : deux interrupteurs « À identifier » et « À éditer » en tête, qui posent ou retirent les tags techniques ; les tags ordinaires en dessous, comme aujourd'hui. Les suggestions ne proposent jamais les tags techniques.
5. Hors de `stash_folder`, ou sans Stash réglé : rien ne change.

## Critères d'acceptation

- [x] Barre de filtre : « ✂ À éditer » et « 🔍 À identifier » en premier, style distinct ; « Edit » et « Identify » absents des tags ordinaires ; les autres tags de Stash ensuite.
- [x] « ✂ À éditer » + case « Masquer les non identifiées » : comportement de BL-153 inchangé. « 🔍 À identifier » : vidéos taguées « Identify ».
- [x] Fenêtre 🏷 : deux interrupteurs qui écrivent les tags techniques dans Stash ; tags techniques absents des tags ordinaires et des suggestions ; atteignable à la manette.
- [x] Les noms réglés (`stash_tag_edit`, `stash_tag_identify`) sont respectés, comparaison insensible à la casse.
- [x] Menu manette (section « À éditer ») : « 🔍 À identifier » ajouté.
- [x] Tests (faux Stash) pour le filtrage des tags techniques côté backend s'il y en a ; vérification dans le navigateur. (Filtrage dans la page seule, aucun changement backend : vérifié dans le navigateur avec des données Stash simulées.)
- [x] Doc : guide FR + EN (section Stash, tableau des tags) ; changelogs.
