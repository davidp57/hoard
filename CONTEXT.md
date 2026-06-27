# Hoard

Navigateur de filesystem brut et lecteur multimédia auto-hébergé. Le glossaire ci-dessous
fixe le vocabulaire métier (ce que sont les concepts, pas comment ils sont implémentés).

## Language

**Galerie** :
Séquence ordonnée d'éléments prévisualisables — principalement des images, plus
d'éventuels passagers — lue comme un média unique, avec reprise à la position
courante. Deux supports : une *archive* (`.cbz`/`.cbr`/`.zip`, séquence plate) ou un
*dossier* — qui peut s'étendre récursivement à travers ses sous-dossiers,
l'arborescence étant aplatie en une seule séquence. Une galerie ne contient aucune
vidéo. Les deux supports partagent la même identité visuelle (icône) et la même
logique de lecture/reprise.
_Avoid_: diaporama, album, planche

**Passager** :
Fichier non-image présent dans une galerie (PDF, texte, audio, archive). Il occupe
une position dans la séquence comme une image, et est représenté par un aperçu
(1ʳᵉ page du PDF, extrait du texte) ou, à défaut, une icône générique. Sa présence
ne casse pas la galerie.
_Avoid_: pièce jointe, annexe

**Média** :
Élément lisible par le player et porteur d'un état de lecture (vidéo, audio, PDF,
galerie). S'oppose à un simple fichier « autre » ou à un dossier de navigation pur.
