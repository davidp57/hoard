# BL-069 — Socle galerie-dossier lisible

Status: ✅ done
Type: feat
Parent: FEAT-GALLERY ([PRD](../PRD.md))
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`

## What to build

Faire qu'un dossier d'images se comporte de bout en bout comme une **galerie** lisible,
sur le modèle des archives existantes. Un dossier éligible (> 3 images comptées
récursivement, aucune vidéo nulle part) est détecté comme galerie ; l'ouvrir affiche
la première image (ou la position de reprise) au lieu de la liste, et on parcourt les
images les unes après les autres avec sauvegarde continue de la position. Le dossier
apparaît dans la liste parente comme un média (icône 🖼️, barre de progression, %,
état non-vu / en-cours / vu au seuil 90 %).

L'ordre de la séquence aplatit l'arborescence : parcours profondeur-d'abord, fichiers
du niveau courant avant les sous-dossiers, tri naturel (numérique-aware).

API : `/api/files` expose un dossier-galerie avec `media_type: "gallery"` (+ `progress`
et un `folder_state` dérivé de sa propre progression) ; nouvel endpoint
`/api/gallery/list?path=` retourne la séquence ordonnée, calqué sur `/api/archive/list`.
Les images sont servies par `/api/file` existant. Reprise ancrée sur le chemin du
dossier (`position` = index, `duration` = total ; schéma `progress` inchangé).

## Acceptance criteria

- [ ] Un dossier > 3 images sans vidéo est renvoyé par `/api/files` avec `media_type: "gallery"` et un `progress`
- [ ] Un dossier avec une vidéo, ou ≤ 3 images, reste un dossier normal
- [ ] Les images en sous-dossiers sont comptées récursivement dans le seuil
- [ ] `/api/gallery/list` retourne la séquence aplatie dans l'ordre (profondeur, niveau courant avant sous-dossiers, tri naturel)
- [ ] Ouvrir une galerie affiche la 1ʳᵉ image (ou la reprise), jamais la liste ; prev/next parcourt la séquence
- [ ] La position est sauvée en continu sur le chemin du dossier et restaurée à la réouverture
- [ ] La galerie s'affiche dans la liste avec icône 🖼️, barre + % et état non-vu/en-cours/vu (seuil 90 %)
- [ ] Tests API : détection, séquence/ordre, reprise ; `ruff` + `pytest` au vert

## Blocked by

None — can start immediately
