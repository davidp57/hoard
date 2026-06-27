# Lot FEAT-GALLERY — Galeries d'images (dossier comme média opaque)

Status: ✅ done
Branch: feature/gallery → PR #31 (merged) → develop

## Problem Statement

Quand un dossier ne contient que des images (un scan, un set de photos, une planche),
l'utilisateur veut le consulter comme **une seule chose** qu'on lit page par page —
exactement comme il regarde une vidéo, avec reprise à l'endroit où il s'était arrêté.
Aujourd'hui ce n'est pas le cas : entrer dans un tel dossier affiche la **liste** de
ses fichiers, l'état de lecture n'apparaît pas dans la liste parente (un dossier
d'images est toujours « non vu »), et il faut ouvrir chaque image une par une sans
mémoire de la progression sur l'ensemble.

Hoard sait pourtant déjà faire exactement ça — mais uniquement pour les **archives**
(`.cbz`/`.cbr`/`.zip`) : on ouvre le paquet, on voit la première image, on parcourt,
et la position est sauvée. Le besoin est d'étendre ce comportement aux dossiers.

## Solution

Introduire le concept de **galerie** (voir `CONTEXT.md`) : une séquence ordonnée
d'éléments prévisualisables, lue comme un média unique avec reprise, dont l'archive et
le dossier d'images sont deux supports unifiés.

Un dossier éligible se comporte alors comme une vidéo :
- il s'affiche dans la liste parente avec une icône dédiée (🖼️), une barre de
  progression, un pourcentage et un état non-vu / en-cours / vu ;
- l'ouvrir affiche **la première image** (ou la reprise), pas la liste ;
- on parcourt les images les unes après les autres, la position est sauvée en continu ;
- une **barre de thumbnails** sert à la fois de seek (clic = saut) et de gestion
  d'image fine à la souris (X = supprimer l'image, `>` = déplacer l'image).

Un fichier non-image égaré dans la galerie (PDF, texte…) devient un **passager** :
il garde sa place dans la séquence et reçoit un aperçu, plutôt que de disparaître
derrière l'opacité de la galerie.

## User Stories

1. En tant qu'utilisateur, quand un dossier ne contient que des images, je veux qu'il
   apparaisse dans la liste comme un média unique (icône galerie), pour le traiter
   comme une vidéo plutôt que comme un dossier à parcourir.
2. En tant qu'utilisateur, je veux voir l'état de lecture d'une galerie dans la liste
   (non-vu / en-cours avec barre et %, vu), pour savoir d'un coup d'œil où j'en suis.
3. En tant qu'utilisateur, en ouvrant une galerie, je veux voir tout de suite la
   première image (ou celle où je m'étais arrêté), sans passer par une liste.
4. En tant qu'utilisateur, je veux parcourir les images d'une galerie les unes après
   les autres (clavier, pad, gestes), pour la lire confortablement.
5. En tant qu'utilisateur, je veux que ma position dans la galerie soit sauvée
   automatiquement, pour reprendre plus tard là où j'en étais.
6. En tant qu'utilisateur lisant un scan rangé en chapitres (sous-dossiers), je veux
   que toutes les pages s'enchaînent dans le bon ordre comme une seule séquence.
7. En tant qu'utilisateur, je veux une barre de thumbnails sous la galerie, pour voir
   où je suis et sauter directement à une image en cliquant dessus.
8. En tant qu'utilisateur sur desktop, je veux pouvoir supprimer une image précise
   depuis la barre de thumbnails (icône X au survol), pour retirer une image ratée.
9. En tant qu'utilisateur sur desktop, je veux pouvoir déplacer une image précise
   depuis la barre de thumbnails (icône `>` au survol), pour la ranger ailleurs.
10. En tant qu'utilisateur, je veux que les raccourcis clavier/pad de déplacement et
    de suppression agissent sur la galerie entière (comme pour une vidéo), pour gérer
    le dossier d'un bloc.
11. En tant qu'utilisateur, je veux marquer manuellement une galerie comme vue / non
    vue (`W`), comme pour une vidéo.
12. En tant qu'utilisateur en plein écran, je veux qu'après avoir supprimé ou déplacé
    une galerie, la suivante s'ouvre automatiquement, comme pour une vidéo.
13. En tant qu'utilisateur, je veux que la première image s'affiche immédiatement,
    sans attendre la génération des vignettes de la barre de thumbnails.
14. En tant qu'utilisateur ayant un PDF ou un fichier texte égaré dans un dossier
    d'images, je veux qu'il reste visible et prévisualisable dans la galerie, pour ne
    pas le perdre derrière la visionneuse.
15. En tant qu'utilisateur, je veux survoler un passager dans la barre de thumbnails
    et en voir un aperçu (1ʳᵉ page du PDF, extrait du texte), pour l'identifier.
16. En tant qu'utilisateur, je veux que les galeries-dossiers et les galeries-archives
    se présentent et se lisent de la même façon (même icône, mêmes commandes), pour ne
    pas avoir à apprendre deux comportements.
17. En tant qu'utilisateur, je veux qu'un dossier mixte (images + une vidéo, ou + un
    autre média) reste un dossier normal navigable, pour garder accès à tout son
    contenu.
18. En tant qu'utilisateur en plein écran, je veux pouvoir lire une galerie en plein
    écran avec les gestes tactiles et les raccourcis habituels.

## Implementation Decisions

- **Concept unifié (ADR 0002)** : galerie = séquence ordonnée d'éléments
  prévisualisables ; supports *archive* et *dossier*. La logique de lecture/reprise de
  l'archive (`openArchive`) et celle du dossier convergent vers un chemin commun.
- **Détection (dossier)** : galerie si et seulement si le dossier contient
  (récursivement) **plus de 3 images** et **aucune vidéo**. Sous-dossiers autorisés ;
  galerie détectée au dossier le plus haut éligible.
- **API détection** : `/api/files` expose un dossier-galerie avec
  `media_type: "gallery"` (au lieu de `"other"`), assorti de `progress`, et un
  `folder_state` dérivé de **sa propre** progression (pas de l'agrégat vidéo).
- **API séquence** : nouvel endpoint `/api/gallery/list?path=` retournant la séquence
  ordonnée aplatie (images + passagers, chacun avec son type), calqué sur
  `/api/archive/list`. Ordre : parcours profondeur-d'abord, fichiers du niveau courant
  avant les sous-dossiers, tri **naturel** (numérique-aware).
- **Service des images** : réutilise `/api/file?path=` pour l'image pleine ; nouvel
  endpoint `/api/thumbnail?path=` pour une vignette **downscalée à la volée via
  ffmpeg** (pas de nouvelle dépendance Python, **pas de cache**).
- **Reprise** : `position` = index courant, `duration` = total, ancrés sur le **chemin
  du dossier**. Le schéma SQLite `progress` reste inchangé (index volatil assumé).
- **Opacité** : clic sur une galerie → visionneuse (jamais la liste). Déplacer /
  supprimer au clavier/pad agit sur la galerie entière. La gestion d'image
  individuelle se fait à la souris via la barre de thumbnails (action rare,
  desktop-only — pas de survol sur tactile).
- **Barre de thumbnails** : seek au clic ; au survol d'une vignette, icônes X
  (supprimer l'image) et `>` (déplacer l'image, via le picker de destination
  existant). Chargement **paresseux** (vignettes visibles seulement) ; la première
  image principale s'affiche sans attendre les vignettes.
- **Passagers** : un fichier non-image dans la galerie occupe une position dans la
  séquence. Aperçu rendu **côté client** : PDF 1ʳᵉ page via PDF.js (déjà bundlé), txt
  par extrait ; icône générique pour les autres types en v1.
- **Lecture** : pas d'auto-enchaînement vers l'élément suivant à la fin d'une galerie
  (on s'arrête sur la dernière image, galerie passée « vue »).
- **Icône** : 🖼️ pour toute galerie (dossier comme archive).

## Testing Decisions

- **Principe** : tester le comportement externe (réponses API), pas l'implémentation.
  Le frontend single-file n'a pas de harness → validation par `node --check` + revue
  visuelle (cohérent avec les lots précédents).
- **Prior art** : les tests d'archives et d'images de `tests/test_api.py` (listing
  d'archive, service d'image, `media_type` par extension, progression non-vidéo) sont
  le modèle direct.
- **Détection** (`/api/files`) : dossier > 3 images sans vidéo → `media_type:
  "gallery"` + `progress` ; dossier avec une vidéo → dossier normal ; ≤ 3 images →
  dossier normal ; images réparties en sous-dossiers → comptées récursivement.
- **Séquence** (`/api/gallery/list`) : ordre profondeur-d'abord / niveau courant avant
  sous-dossiers / tri naturel ; présence des passagers avec leur type.
- **Vignettes** (`/api/thumbnail`) : 200 + `Content-Type image/*` ; rejet
  path-traversal (chemin hors `MEDIA_ROOT`).
- **Reprise** : couverte par les tests de progression existants (chemin = dossier).
- **Qualité** : `ruff check` + `ruff format --check` + `pytest` au vert.

## Out of Scope

- **Reprise par chemin d'image** (robustesse aux ajouts/suppressions) — on assume
  l'index volatil.
- **Agrégat d'état mixte** : un conteneur normal (avec vidéo) ne compte pas
  l'avancement des galeries imbriquées dans son `folder_state` (v1).
- **Navigation libre dans une galerie** : pas de mode liste, pas d'accès aux
  sous-chapitres en tant qu'entrées séparées.
- **Gestion d'image fine sur tactile** (pas de survol) — desktop/souris uniquement.
- **Aperçu réel des passagers audio / archive** — icône générique en v1 (PDF + txt
  seulement en aperçu réel).
- **Lecture intégrale d'un passager** (ouvrir le vrai lecteur PDF depuis la galerie) —
  l'aperçu suffit ; pour l'exploiter, déplacer le fichier hors de la galerie.
- **Cache de vignettes** (mémoire ou disque) — à n'ajouter que si le re-scroll de très
  grandes galeries pose problème.

## Further Notes

- Décision actée dans `docs/adr/0002-galleries.md` ; vocabulaire dans `CONTEXT.md`
  (*galerie*, *passager*).
- Opportunité de refactoring : faire converger `openArchive` et la nouvelle lecture de
  dossier-galerie vers une logique de visionneuse commune (la barre de thumbnails et la
  reprise sont partagées ; seule la source des images diffère).
- Lockstep doc : `docs/user-guide.*` + `docs/developer.*` (nouveaux endpoints) +
  `docs/changelog-user.fr.md` + `CHANGELOG.md`.
