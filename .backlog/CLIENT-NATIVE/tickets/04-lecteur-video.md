# BL-109 — Lecteur vidéo : trancher le chemin de rendu

Status: ⬜ ready
Type: feat
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 02
Files: `client/lib/`

## What to build

Le lecteur : lecture depuis `/api/file`, reprise et sauvegarde de position,
sous-titres, gestes tactiles. Mais **le préalable est un choix d'architecture**
que BL-104 a rendu obligatoire.

### Le problème mesuré

`media_kit` ne signale pas ses nouvelles images à Flutter. La vidéo n'avance que
lorsque l'interface est repeinte pour une autre raison : **8 images par seconde
au repos, 25 dès qu'une animation tourne à l'écran**. mpv, lui, ne perd aucune
image — il remplit fidèlement une texture que personne ne redessine.

Ce n'est pas un défaut de Flutter ni du décodage. `hwdec=auto-safe` donne
`vaapi-copy` à 102 % d'un cœur, moins cher que le logiciel. C'est le pont entre
mpv et la texture Flutter qui est en cause.

### Les deux voies, à départager par la mesure

**(a) mpv dessine sa propre surface.** L'interface Flutter est disposée autour,
ou par-dessus en surimpression. Supprime le problème à la racine et c'est ce que
font les lecteurs qui marchent. Coût : la composition devient délicate — ordre
d'empilement, plein écran, dialogues au-dessus de la vidéo — et sous Gamescope
il faudra vérifier que deux surfaces cohabitent.

**(b) Garder la texture, forcer le redessin pendant la lecture.** Quelques
lignes, effet immédiat, déjà éprouvé dans le spike. Coût : la machine dessine en
continu tant qu'une vidéo joue, ce qui se paie en batterie sur une console
portable — et ne règle rien pour la galerie, qui a le même pont.

Ne pas trancher sur le papier. Prototyper (a) et mesurer la consommation des
deux sur le Deck, batterie en charge décroissante, même fichier, même durée.

### Ce qui est déjà acquis et n'est pas à re-décider

- **`hwdec=auto-safe`**, pas `vaapi` forcé : forcer fait retomber mpv en
  logiciel, puisque le partage GPU n'existe pas avec la texture.
- **Les identifiants passent à mpv en en-tête**, pas dans l'URL — vérifié, les
  `httpHeaders` de `media_kit` atteignent bien libmpv.
- **Mesurer le rendu, pas le décodage.** Les compteurs de mpv décrivent mpv :
  ils affichaient zéro perte pendant que l'image se traînait. La grandeur utile
  est le nombre de trames rendues par Flutter
  (`SchedulerBinding.addTimingsCallback`). Et `estimated-vf-fps` est le débit de
  la **source**, pas celui de l'affichage.

## Acceptance criteria

- [ ] Une mesure comparée des deux voies sur le Deck : images réellement
      rendues, et consommation batterie sur une durée identique
- [ ] La voie retenue tient le débit source sans animation parasite à l'écran
- [ ] Reprise et sauvegarde de position partagées avec l'interface web
- [ ] Sous-titres et gestes tactiles
- [ ] La décision et sa mesure consignées dans l'ADR 0003
