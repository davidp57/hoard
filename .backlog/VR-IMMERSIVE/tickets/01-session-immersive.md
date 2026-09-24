# BL-136 — Session immersive depuis le lecteur

Status: 🧑 waiting-human — en pause : le navigateur du Frame n'expose pas WebXR (testé le 2026-09-24, voir le PRD)
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`, `docs/developer.en.md`

## Problem

Sur le Steam Frame, le mode côte à côte arrive dans une fenêtre plate : pas de
relief. Voir le [PRD](../PRD.md).

## What was built

- Bouton **XR** dans la barre du lecteur, visible seulement si
  `isSessionSupported('immersive-vr')` répond oui (réévalué sur `devicechange`).
- `enterXr()` : `requestSession` en premier `await` (le navigateur exige le geste
  de l'utilisateur), `makeXRCompatible`, `XRWebGLLayer`, espace de référence
  `local`.
- Second programme WebGL (`XR_FRAG`) sur le même contexte et la même texture que
  les modes plats ; rayon construit depuis la projection de l'œil, orienté par la
  tête, recentrage et convergence en lacet.
- Envoi de la texture à chaque image décodée, avec repli sur l'horloge de la
  vidéo si `requestVideoFrameCallback` se tait derrière la session.
- Manettes du casque : gâchette / A / X lecture-pause, stick du seek moyen avec
  répétition, clic stick recentre, B / Y sort.
- Sortie : retour au mode plat d'avant ; fermeture du lecteur, flux transcodé et
  perte de contexte ferment la session.

## Acceptance criteria

- [x] Bouton caché quand le navigateur n'a pas de casque (Chrome sans casque)
- [x] Avec un `navigator.xr` simulé : chaque œil dessine sa moitié du fichier
- [x] Une tête tournée de 30° décale le centre de 118 px (115 attendus à 90° par
      œil) ; le recentrage le ramène au milieu
- [x] Convergence de même signe que le mode côte à côte plat
- [x] Commandes simulées : A et gâchette basculent la lecture, une pichenette
      avance d'un pas, un maintien de 900 ms en fait trois, B ferme
- [x] Sortie : mode plat d'avant restauré, programme et framebuffer remis
- [x] Fermer le lecteur ferme la session
- [ ] **Sur le Frame** : le bouton apparaît, la session s'ouvre, le relief est là
- [ ] **Sur le Frame** : les manettes répondent dans la session
