# BL-146 — N'ouvrir le lien Steam que si FramePlayerX est fermé

Status: ✅ done — essai concluant sur le Frame le 2026-11-14 (PR #89, v2.9.5)
Lot: [FEAT-FPX-HANDOFF](../PRD.md)

## Quoi

Essai de David le 2026-11-14 (Hoard 2.9.4, `fpx_host` = IP du casque) : la vidéo s'ouvre dans FPX, au bon endroit, et la reprise revient bien dans Hoard.
Mais quand FPX tourne déjà, SteamOS affiche « Impossible de lancer ce jeu, il est déjà lancé » : `playInFpx` ouvre `steam://rungameid/…` à chaque lancement.
La vidéo, elle, part par le port 23554 et s'ouvre quand même.

Au clic, Hoard demande d'abord si FPX répond sur le port 23554, avec un délai court (de l'ordre d'une seconde, pour rester dans l'activation utilisateur qu'exige un lien `steam://`) :

- FPX répond : la vidéo lui est envoyée, **pas de lien `steam://`**. David passe lui-même sur FPX (bouton Steam, FPX, « Reprendre le jeu ») — décision du 2026-11-14, voir BL-145.
- FPX ne répond pas (refusé ou délai dépassé) : comportement actuel, lien `steam://` puis relances pendant environ 20 s.

Forme suggérée : une première tentative de `/api/fpx/play` sans relance, qui répond vite « FPX ne tourne pas » ; la page ouvre alors le lien Steam et relance la demande avec la fenêtre de relance. Un seul aller-retour dans le cas courant.

Comme FPX reste derrière Chromium dans ce cas, l'écran « Lecture dans FramePlayerX » le dit : la vidéo est ouverte dans FPX, passer dessus par le menu Steam.

## Réalisation (2026-11-14, 2.9.5)

`POST /api/fpx/play` prend `wait` (vrai par défaut). Avec `wait: false`, `_fpx_probe` fait une seule tentative par adresse, toutes dans `FPX_PROBE_TIMEOUT` (1 s), et renvoie **503** si FPX n'écoute pas — un code que rien d'autre n'utilise sur cette route (409 = pas configuré, 400 = hors réseau local, 502 = nom introuvable ou injoignable après 20 s).
La page sonde d'abord ; sur 503 seulement, elle ouvre le lien `steam://` et relance avec `wait: true`. Une erreur de nom ou d'hôte s'affiche sans lancer FPX.
Vérifié par pytest et dans le navigateur avec des réponses simulées (FPX lancé, fermé, nom introuvable). Reste l'essai sur le Frame.

## Critères d'acceptation

- [x] FPX joignable : aucun lien `steam://` ouvert, vidéo envoyée, suivi de lecture inchangé.
- [x] FPX injoignable : lien `steam://` ouvert dans le geste de l'utilisateur, puis relances comme aujourd'hui.
- [x] Sonde bornée (casque éteint ou hors réseau : pas plus d'environ une seconde avant le lien Steam).
- [x] Tests backend du mode sans relance (joignable, refusé, délai dépassé).
- [x] Guide FR/EN : quand FPX tourne déjà, il faut passer dessus soi-même.
- [ ] **Essai sur le Frame (David)** : FPX déjà lancé, une vidéo depuis Hoard, plus de message d'erreur Steam.
