# BL-144 — Lancer la lecture dans FramePlayerX depuis Hoard

Status: 🧑 waiting-human — essai sur le Frame par David (livré dans la PR #86, v2.9.2)
Lot: [FEAT-FPX-HANDOFF](../PRD.md)

## Quoi

Décisions 1 à 7 du PRD : réglages, bascule propre à l'appareil, URL signée, ouverture, suivi et retour dans Hoard.

## Critères d'acceptation

- [x] Réglages `fpx_host` et `fpx_steam_gameid` dans Paramètres (avec `applyCfg`), fonction coupée tant que `fpx_host` est vide.
- [x] Bascule « Lire dans FramePlayerX » dans Paramètres (`localStorage['fpx_handoff']`), et exception par vidéo dans le menu contextuel ; atteignable à la manette.
- [x] Bascule active : ouvrir une vidéo (clic, Entrée, A) ouvre le lien `steam://rungameid/<fpx_steam_gameid>` puis appelle `POST /api/fpx/play` ; écran « Lecture dans FramePlayerX » avec titre, position qui avance et bouton « Reprendre ici ».
- [x] Le message envoyé à FPX contient l'URL `/api/file` signée et la position de reprise de `progress`.
- [x] URL signée : acceptée par `/api/file` seulement, refusée si le chemin diffère, si elle a expiré ou si la signature est fausse ; aucune autre route ne l'accepte.
- [x] Suivi : position écrite dans `progress` toutes les 10 s, à la pause et à la fermeture ; passage « vu » au seuil ; fin de suivi sur `{}`, changement d'adresse ou coupure.
- [x] Fin de lecture : l'écran se ferme, la liste se rafraîchit, le curseur reste sur la vidéo.
- [x] FPX injoignable, ou `fpx_host` non privé : erreur claire, rien n'est écrit.
- [x] Tests pytest avec un faux FPX (serveur TCP local qui parle le format du PRD) : message d'ouverture, suivi, `{}` qui termine, coupure, injoignable ; URL signée.
- [x] Doc : guide utilisateur FR + EN (régler `fpx_host` et l'identifiant Steam, comment le trouver, activer la bascule dans le casque) ; doc développeur (routes, protocole, quatrième clé `localStorage`).
- [ ] **Essai sur le Frame (David)** : depuis Hoard dans Chromium, lancer une vidéo, vérifier qu'elle s'ouvre dans FPX à la bonne position, la fermer et noter ce que fait le Frame (retour dans Chromium ou non). La réponse décide de BL-145.
