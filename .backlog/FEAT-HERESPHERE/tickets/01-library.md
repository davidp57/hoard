# BL-142 — Bibliothèque, scan et scènes HereSphere

Status: ⬜ ready
Lot: [FEAT-HERESPHERE](../PRD.md)

## Quoi

Les routes `POST /heresphere`, `POST /heresphere/scan` et `POST /heresphere/scene/<id>`, au format relevé dans le PRD, avec les groupes et le format VR des décisions 3 à 5.

## Critères d'acceptation

- [ ] `POST /heresphere` rend `access: 1` et les groupes « En cours », « Récemment vus », « Non vus », puis un groupe par dossier rapide ; chaque scène y figure par son URL absolue `…/heresphere/scene/<id>`.
- [ ] `POST /heresphere/scan` rend le détail de toutes les scènes listées (titre, durée quand elle est connue, date d'ajout).
- [ ] `POST /heresphere/scene/<id>` rend titre, durée en ms, `projection` / `stereo` / `fov` selon `vr_modes` ou la détection par le nom, et une source média qui pointe sur `/api/file`.
- [ ] Un identifiant qui sort de `MEDIA_ROOT`, ou qui ne désigne pas une vidéo, donne 404 (passe par `safe_path()`).
- [ ] Sans identifiants, une requête est refusée comme le reste de l'API ; avec HTTP Basic, elle passe. Pas de régression sur le refus des écritures cross-site pour le navigateur.
- [ ] Tests pytest sur le format des trois réponses, l'encodage des identifiants et le refus hors racine.
- [ ] Doc : section « FramePlayerX / HereSphere » dans le guide utilisateur (FR + EN), qui dit quelle URL saisir dans FPX et avec quel compte ; routes dans la doc développeur.
- [ ] **Essai sur le Frame** : FPX › Sources › Add source › HereSphere avec l'URL de Hoard, groupes visibles, une vidéo 180° SBS et une vidéo plate lues dans le bon format (David).
