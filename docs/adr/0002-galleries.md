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
- **Détection (dossier)** : galerie ssi le dossier est une **feuille** — **plus de
  3 images**, **aucune vidéo**, et **aucun sous-dossier** (parcours du niveau courant
  seulement, tri naturel). Un dossier qui contient des sous-dossiers est un conteneur
  navigable ; un dossier de galeries affiche donc chaque sous-dossier comme sa propre
  galerie. *(Révisé le 2026-06-27 — voir ci-dessous.)*
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

- Un dossier qui repasse sous le seuil (images supprimées/déplacées) redevient un
  dossier normal au prochain listing.
- Un conteneur normal (avec vidéo) garde son état agrégé sur les vidéos seules ; les
  galeries imbriquées n'entrent pas dans cet agrégat (v1).

## Révision 2026-06-27 — détection « feuille » au lieu de récursive

La détection récursive initiale (aplatir toute l'arborescence en une galerie, détectée
au dossier le plus haut) produisait des galeries inutilisables sur des données réelles :
un dossier contenant N albums devenait **une seule** galerie de milliers d'images. Or
au niveau du système de fichiers, « un manga rangé en chapitres » et « un dossier de
plusieurs albums » sont **structurellement identiques** — aucun signal fiable ne les
distingue.

Décision : une galerie est désormais un **dossier feuille** (sans sous-dossier). Un
dossier contenant des sous-dossiers est un conteneur navigable qui affiche chaque
sous-dossier comme sa propre galerie.

- **Gain** : le cas « dossier de galeries » fonctionne ; comportement prévisible
  (structurel, pas dépendant d'un seuil) ; détection en `O(iterdir)` sans `rglob`
  (résout aussi la préoccupation perf de BL-074 côté détection).
- **Coût assumé** : plus de lecture continue inter-chapitres — un manga en chapitres se
  lit chapitre par chapitre (chaque chapitre est une galerie).
- **Alternative écartée** : plafond de taille (basculer en conteneur au-delà de N
  images) — garderait l'aplatissement pour les petits cas mais introduit un seuil
  arbitraire et un comportement variable selon la taille.
