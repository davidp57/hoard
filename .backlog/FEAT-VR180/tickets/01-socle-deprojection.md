# BL-119 — Socle : déprojection 180°, vue plate et pilotage du regard

Status: ✅ done
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

Un fichier 180° SBS s'ouvre aujourd'hui comme une vidéo ordinaire : deux images
accolées, chacune déformée par sa projection équirectangulaire. Il n'existe aucun
chemin de rendu capable de redresser l'hémisphère.

Ce ticket est **une porte** : au-delà du rendu, il mesure sur les vrais fichiers ce
que le navigateur décode et ce que coûte l'envoi de texture à 7680×3840. Les trois
tickets suivants supposent cette réponse connue.

## What to build

### Rendu

- Un `<canvas id="vr-canvas">` superposé au `<video>` dans `#video-container`.
  Le `<video>` reste en place et continue de porter la lecture ; il est seulement
  masqué visuellement quand le mode VR est actif.
- Un programme WebGL2 minimal : un quad plein écran, un fragment shader qui pour
  chaque pixel
  1. construit la direction du rayon depuis `yaw`, `pitch` et le champ de vision,
  2. la convertit en `(longitude, latitude)`,
  3. la ramène dans les bornes UV de l'œil visé (`uvOrigin`, `uvSize`) sachant
     l'angle couvert par l'image (`ih_fov`, `iv_fov`),
  4. échantillonne la texture, et rend du noir hors de l'hémisphère.
- Les bornes UV sont des uniformes : l'œil gauche est `(0,0)→(0.5,1)`, le droit
  `(0.5,0)→(1,1)`. Le fichier anamorphosé (œil 1920×2160) n'est donc pas un cas
  particulier — seule compte la zone, pas la forme des pixels.
- Envoi de texture dans `requestVideoFrameCallback`, avec repli sur
  `requestAnimationFrame` là où il n'existe pas.

### Pilotage du regard

- **Stick droit de la manette** en priorité, branché sur la boucle Gamepad existante :
  vitesse angulaire proportionnelle à la déflexion, zone morte, sensibilité réglable
  (valeur en dur ici, exposée par BL-122).
- Souris (glissé) et tactile (un doigt) en complément.
- Tangage borné à ±90°, lacet borné à ±90° (on ne regarde pas derrière soi dans un
  hémisphère), recentrage sur un appui.
- **En mode VR, le glissé d'un doigt regarde autour** : les gestes de seek et de
  volume sont désactivés tant que le mode est actif. Ils restent atteignables au
  clavier, à la manette et par les boutons du lecteur.

### Activation

- Bascule manuelle dans la barre du lecteur et par raccourci clavier, sans détection
  automatique — la détection est le sujet de BL-121.
- Sortie du mode VR : le `<canvas>` est caché, le `<video>` réapparaît, les gestes
  reprennent leur rôle normal.

## Écart assumé par rapport à l'énoncé

L'énoncé disait « les gestes de seek et de volume sont désactivés » en mode VR.
Livré : **seuls les glissés** changent de rôle. Le conflit réel porte sur le
glissé — l'avance, le volume et la luminosité en sont tous les trois. Les
frappes (lecture/pause au centre, avance par double-frappe en zone latérale) ne
disputent rien au regard et restent actives : les désactiver aurait retiré des
commandes sans qu'aucun conflit ne l'exige.

## Mesures relevées

Mesuré **sur le code livré**, pas sur le prototype, et au pixel plutôt qu'à l'œil.

**Géométrie** — une mire équirectangulaire synthétique (méridiens et parallèles
tous les 15°) traverse le rendu du lecteur, canvas 1001×751 :

| contrôle | attendu | mesuré |
|---|---|---|
| échelle angulaire, lacet 22,5° / −30° / 40° | colonne du méridien 0 | écart −0,9 / −0,7 / −1,5 px |
| centre de l'image à lacet et tangage nuls | croisement blanc | `[255,255,255]` |
| rectitude du méridien 0 à lacet 22°, tangage 17° | une droite | déviation max **0,42 px** sur 13 points |
| au-delà de l'hémisphère (lacet 89°) | noir | `[0,0,0]` |
| mode côte à côte | deux yeux distincts | moitiés différentes (écart moyen 18,9/canal sur un vrai fichier) |

Le méridien 0 est un grand cercle : une projection rectilinéaire correcte le
rend rigoureusement droit quel que soit l'angle. C'est le contrôle qui tranche,
et il passe.

**Décodage et texture**, fichier HEVC 7200×3600 à 60 images/s servi par
`/api/file` :

- décodage **59 images par seconde, 0 perdue** (294 images en 4,97 s, confirmé
  sur trois relevés) ;
- `MAX_TEXTURE_SIZE` = **16384**, donc le 7680 le plus large de la médiathèque
  passe sans redimensionnement ;
- la texture vidéo s'échantillonne correctement (100 % de pixels non noirs,
  luminance moyenne 105, aucune erreur GL).

**Portée de cette mesure** : un navigateur, une machine. Elle ne dit rien de
Firefox ni du navigateur du Steam Deck, et il n'y a pas de repli côté serveur —
`/api/transcode` ne transcodera jamais du 8K60. La mesure sur la cible reste à
faire par l'utilisateur.

**Défaut trouvé par la mesure, et corrigé.** À champ de vision horizontal fixe,
le vertical suit le rapport d'image : le panneau lecteur mesuré à 543×1695 en
vue partagée le poussait à 144°, ce qui déforme. Le vertical est borné à 110°
(`VR_MAX_VFOV`), l'horizontal étant dérivé de lui au-delà.

**Deux instruments écartés en route**, à ne pas refaire : `gl.finish()` ne
synchronise pas dans Chromium — le temps mesuré ne bougeait pas entre une
surface de 320×240 et une de 3840×2160 — et un onglet masqué ne rend rien, donc
toute mesure de débit y est nulle par construction. Seul
`EXT_disjoint_timer_query_webgl2` a produit des chiffres qui réagissent à la
taille.

## Acceptance criteria

- [x] Une mire équirectangulaire 180° SBS s'affiche sans distorsion : méridien 0
      droit à 0,42 px près, échelle angulaire juste à moins de 1,5 px
- [x] Le lacet et le tangage répondent au stick droit, à la souris et au doigt
- [x] Le regard ne sort pas de l'hémisphère, et le hors-champ est noir et non étiré
- [x] Le fichier anamorphosé se déprojette lui aussi : le shader ne connaît que
      les bornes UV de l'œil et l'angle couvert, jamais la forme des pixels
- [x] La lecture, la position, la progression et les sous-titres sont inchangés :
      le canvas est en `pointer-events:none` et le `<video>` reste dessous
- [x] En mode VR, un glissé regarde autour et ne fait ni seek ni volume ; hors mode
      VR, les gestes sont exactement ceux d'avant
- [x] Sortir du mode VR restitue le lecteur normal (vérifié : canvas retiré,
      `<video>` visible, aucune erreur console)
- [x] Les mesures ci-dessus sont relevées et inscrites

## Défauts trouvés en revue, avant la PR

La revue a trouvé **trois défauts réels**, invisibles pour la porte de qualité
(tests au vert, aucune erreur console) parce qu'ils sont frontend. Les deux
premiers sur le diff local avant la PR, le troisième par la passe « historique »
de la revue de PR, qui lit ce que l'historique git des lignes touchées révèle.

1. **Écran figé en activant le mode VR sur une vidéo en pause.** L'envoi de texture
   ne se faisait que dans le rappel `requestVideoFrameCallback`, or une vidéo en
   pause ne présente aucune image nouvelle : le rappel n'arrivait jamais et la vue
   montrait ce que la texture contenait avant — du noir à la première activation.
   Prouvé en peignant la texture en rouge uni puis en réactivant le mode : rouge à
   255/0/0 sur toute la surface. Corrigé par un envoi immédiat avant la mise en
   attente ; re-mesuré, la vue affiche l'image (173/125/104).
2. **Boucles d'envoi cumulées à chaque bascule.** `setVrMode` relançait la pompe à
   chaque appel, et la boucle ne s'arrêtait qu'en sortant du mode VR : passer
   `flat` → `sbs` laissait tourner l'ancienne **et** en démarrait une nouvelle.
   Trois activations donnaient trois envois de 7200×3600 par image. Corrigé par un
   jeton de génération. Mesuré en déclenchant les rappels à la main (un onglet
   masqué n'en présente aucun) : 3 rappels armés, **1 seul se réarme**, et toujours
   1 à l'image suivante.

3. **La barre de commandes disparaissait sous le canvas en plein écran**, en mode
   `flat` — le mode `sbs` masque les incrustations, pas celui-là. Trouvé par la
   passe « historique » de la revue de PR : le canvas était à `z-index: 2`, au
   dessus du `z-index: 1` qu'un commit ancien avait donné à `#controls` en plein
   écran, avec pour commentaire *« ensure controls (and seekbar hit area) are
   above video »*. Mesuré : 132 px de recouvrement, soit la barre entière. Les
   clics passaient (`pointer-events: none`), mais à l'aveugle. Le canvas descend
   à `z-index: 0` et passe avant les incrustations dans le DOM — au-dessus du
   `<video>`, qui n'est pas positionné, en dessous de tout le reste. Vérifié par
   l'ordre de peinture : `seekbar-wrap → controls → vr-canvas → video`.

Deux autres points, plus légers, corrigés dans la foulée : le message « 🥽 180°
plat » s'affichait même quand l'initialisation avait échoué (il annonçait un mode
qui n'était pas actif), et une perte de contexte graphique laissait le canvas noir
définitivement — elle éteint désormais le mode et oublie l'état pour que
l'activation suivante reconstruise.

## Non couvert par un test automatisé

Le dépôt n'a pas de banc de test JavaScript — les 357 tests portent sur l'API. Ce
ticket est entièrement frontend, donc il n'ajoute aucun test. La vérification est
la mire mesurée au pixel décrite ci-dessus, rejouable depuis la console. BL-121
ajoutera des tests, lui : il touche au backend.
