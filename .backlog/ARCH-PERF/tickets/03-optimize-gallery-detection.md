# BL-074 — Optimiser le coût de détection des galeries dans `/api/files`

Status: ✅ done
Type: chore
Parent: ARCH-PERF ([PRD](../PRD.md))
Files: `backend/main.py`

> **Résolu (2026-06-27)** par le passage à la détection « galerie = dossier feuille » :
> `is_gallery()` ne fait plus de `rglob` récursif, juste un `iterdir()` au niveau courant
> (arrêt au premier sous-dossier ou première vidéo). Le coût par dossier au listing est
> donc supprimé. Reste uniquement la récursion *préexistante* de `get_folder_state()`
> (agrégat vidéo), non aggravée par les galeries — à rouvrir séparément si elle pose
> problème un jour. Le piège « early-exit sur le compte d'images » documenté ci-dessous
> reste valable comme garde-fou.

## Contexte (déclencheur)

À ouvrir si un jour **« ça raaaaame ! »** au listing d'un dossier contenant beaucoup
de sous-dossiers volumineux.

La détection des galeries (introduite par le lot `FEAT-GALLERY`, BL-069) appelle
`is_gallery()` sur **chaque** sous-dossier affiché par `/api/files`, et chaque appel
fait un `folder.rglob("*")` (parcours récursif complet). Pour les dossiers **non**
galerie, on fait même **deux** parcours récursifs : un dans `is_gallery()` et un dans
`get_folder_state()`. Sur une arborescence profonde / large, lister un dossier peut
donc relancer N parcours profonds → latence sensible sur NAS lent.

## Piège à NE PAS reproduire

L'« early-exit » naïf (retourner `True` dès `image_count > 3`) est **incorrect** :
`rglob` ne garantit pas l'ordre, donc un dossier `4 images + 1 vidéo` pourrait être
classé galerie si la vidéo est rencontrée après la 4ᵉ image — ça casse l'invariant
« une galerie ne contient aucune vidéo ». Le parcours complet est nécessaire pour
*prouver* l'absence de vidéo. (Le seul early-exit sûr, déjà en place, est
`return False` dès la première vidéo.) Suggestion déjà déclinée en revue Sourcery
(PR #31).

## Pistes (par ordre de préférence)

1. **Un seul parcours partagé** : fusionner `is_gallery()` et `get_folder_state()` en
   un unique `rglob` par dossier qui calcule à la fois (images comptées, vidéo
   présente, état d'avancement). Meilleur rapport gain/risque, comportement inchangé.
2. **Différer la détection** : ne pas décider au listing ; détecter la galerie
   seulement à l'ouverture du dossier (un `rglob` au clic au lieu d'un par entrée).
   Inconvénient : l'icône 🖼️ / la barre de progression n'apparaîtraient plus dans la
   liste sans un appel séparé.
3. **Borner** : limiter la profondeur ou le nombre de fichiers inspectés avant
   d'abandonner la détection.
4. **Cache serveur** par dossier (invalidé au changement de contenu).

## Acceptance criteria

- [ ] Lister un dossier ne déclenche au pire qu'**un** parcours récursif par sous-dossier
- [ ] Comportement de détection inchangé (mêmes dossiers classés galerie / non galerie)
- [ ] Aucune régression sur l'état `folder_state` des dossiers vidéo
- [ ] L'invariant « galerie = aucune vidéo » reste garanti (pas d'early-exit sur le compte d'images)
- [ ] `ruff` + `pytest` au vert

## Blocked by

None — recommandé après BL-041 (le code de listing/détection pourrait être déplacé lors du découpage de `main.py`)
