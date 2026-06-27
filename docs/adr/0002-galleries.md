---
status: accepted
date: 2026-06-27
---

# Galeries : un dossier d'images est un média opaque

Hoard sait déjà lire une **archive** (`.cbz`/`.cbr`/`.zip`) comme une séquence
d'images avec reprise (position ancrée sur le chemin de l'archive). On généralise ce
comportement aux **dossiers** d'images : un dossier éligible devient une *galerie* —
un média unique, lu page par page, avec reprise — au lieu d'un conteneur de
navigation listant ses fichiers. Voir le glossaire (`CONTEXT.md`) pour les termes
*galerie* et *passager*.

## Décision

- **Concept unifié** : une *galerie* est une séquence ordonnée d'éléments
  prévisualisables (surtout des images), de support **archive** ou **dossier**. Les
  deux partagent la même logique de lecture/reprise et la même icône (🖼️).
- **Détection (dossier)** : galerie ssi le dossier contient (récursivement) **plus de
  3 images** et **aucune vidéo**. Les sous-dossiers sont autorisés ; la galerie est
  détectée au dossier le plus haut éligible et aplatit l'arborescence en une seule
  séquence (parcours profondeur d'abord, fichiers du niveau courant avant les
  sous-dossiers, tri naturel).
- **Opacité** : ouvrir une galerie affiche la première image (ou la reprise), jamais
  la liste. Les actions clavier/pad (déplacer/supprimer) portent sur la galerie
  entière, comme pour une vidéo. La gestion d'image individuelle passe par la barre de
  thumbnails (souris au survol), considérée comme une exception rare.
- **Reprise par index** : `position` = index courant, `duration` = total, ancrés sur
  le chemin du dossier. Le schéma SQLite `progress` reste inchangé.
- **Passagers** : un fichier non-image (PDF, texte, audio, archive) présent dans une
  galerie n'est pas exclu — il occupe une position dans la séquence avec un aperçu, ce
  qui évite tout média caché derrière l'opacité.

## Alternatives écartées

- **Reprise par chemin d'image** (robuste aux ajouts/suppressions) : écartée pour la
  simplicité et la cohérence avec l'archive ; en pratique on ne réorganise pas une
  galerie en cours de lecture. Conséquence assumée : l'index est volatil si le contenu
  du dossier change.
- **Exclure de la galerie tout dossier contenant un média non-image** (pour ne rien
  cacher) : écartée au profit du concept de *passager*, qui rend le média visible dans
  la galerie plutôt que d'en faire un dossier de navigation.
- **Navigation libre dans une galerie** (mode liste, accès aux sous-chapitres) :
  écartée — la galerie est opaque par choix ; le seek se fait via la barre de
  thumbnails.

## Conséquences

- Les sous-dossiers d'une galerie (chapitres) ne sont jamais des entrées navigables.
- Un dossier qui repasse sous le seuil (images supprimées/déplacées) redevient un
  dossier normal au prochain listing.
- Un conteneur normal (avec vidéo) garde son état agrégé sur les vidéos seules ; les
  galeries imbriquées n'entrent pas dans cet agrégat (v1).
