# BL-086 — Menu contextuel manette (Select)

Status: ✅ done
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

La barre de tri, les actions de ligne et la moitié de l'en-tête n'ont aucun chemin
manette. Le tri n'a même pas de chemin clavier.

## Implementation Decisions

**Select** plutôt que LB/RB : ces deux-là sont sautés par la boucle de détection
(`if (i === 4 || i === 5) continue`), ce sont des modificateurs purs. Leur donner
une action supposerait de la déclencher au relâchement sous condition qu'aucun
autre bouton n'ait été pressé — un délai perçu, et une règle de plus à connaître.
Select fait aujourd'hui doublon avec Start dans le browser : il est libre.

## What to build

- **Overlay `gp-menu`**, ouvert par Select depuis le browser, navigable `D↑`/`D↓`,
  `A` valide, `B` ferme. Rendu et navigation calqués sur `gp-overlay`.
- **Deux sections**, la seconde n'apparaissant que si le curseur est sur une entrée :
  - *Liste* — Tri (les 5 critères, avec le critère courant marqué), Sens du tri,
    Filtre par tag, Nouveau dossier, Rafraîchir, Recherche, Accueil,
    Téléchargements, Réglages, Aide manette
  - *Entrée au curseur* — Ouvrir, Marquer vu / non vu, Renommer, Tags, Épingler,
    Déplacer, Supprimer
- Les lignes qui ne s'appliquent pas à l'entrée (Épingler sur un fichier) ne sont
  pas affichées plutôt que grisées.
- Le menu se ferme sur validation, et l'action s'exécute sur l'entrée qui était
  sous le curseur à l'ouverture.

## Acceptance criteria

- [x] Select ouvre le menu depuis la liste, B le ferme
- [x] Les 5 critères de tri et le sens sont applicables au pad
- [x] Renommer, Tags, Épingler, Déplacer, Supprimer, Marquer vu sont applicables
      à l'entrée au curseur
- [x] Le critère de tri courant est visuellement marqué
- [x] La section entrée disparaît quand aucun curseur n'est posé
- [x] Le menu n'apparaît pas par-dessus un modal ou le player
