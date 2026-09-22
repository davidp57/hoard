# BL-134 — La convergence au stick, proportionnelle

Status: ✅ done
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

Au champ juste de 45°, l'image est **2,4× plus agrandie** qu'à l'ancien défaut
de 90° — et tout désalignement entre les deux yeux l'est avec elle. Le pas du
D-pad à 1,2°/s et la borne à ±3° ne suffisaient plus à caler le regard.

## What was built

- Convergence sur le **stick gauche gauche/droite sous R2**, axe qui était libre
  (sous R2 l'avance/recul est déjà supprimée), **proportionnelle à la
  déflexion**, 4°/s à fond de course.
- Le **D-pad garde son pas lent** pour le dernier dixième.
- Borne de ±3 à **±8°**. Les 3 venaient d'une règle de pouce qui mordait avant
  que l'image ne soit calée.

## Acceptance criteria

- [x] 0,25 s à fond de course donnent exactement 1,00°
- [x] Les bornes tiennent à ±8 dans les deux sens
- [x] Une image à 20 % de course donne 0,013° — le réglage fin survit
- [x] Le pas du D-pad répond toujours
- [x] Le stick sous R2 ne touche ni au zoom (axe vertical) ni à la lecture
- [x] Éprouvé par la boucle de scrutation avec une manette simulée, pas en
      appelant le gestionnaire à la main
