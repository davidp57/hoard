# BL-133 — Le champ de vision par défaut, et son nom

Status: ✅ done
Type: fix
Files: `backend/main.py`, `frontend/index.html`, `docs/user-guide.*.md`, `tests/test_api.py`

## Problem

Le défaut de 90° donnait une profondeur fausse sur des lunettes qui présentent
environ 45° à un œil, et le libellé « Champ de vision VR » se lisait comme un
zoom, si bien que rien n'invitait à y mettre la bonne valeur.

## What was built

- Défaut à **45°**, côté serveur comme côté client.
- **Migration à un coup** derrière un marqueur (`vr_fov_default_45_done`), sur
  le modèle de celle de BL-125 : un 90 stocké est presque sûrement l'ancien
  défaut réécrit par le formulaire, qui poste tous les champs d'un coup, et
  laissé là il masquerait le nouveau à jamais.
- Libellé **« Champ de vision de l'écran »**, description qui dit ce qu'il faut
  y mettre et ce qu'on voit quand c'est trop grand ou trop petit.
- Un paragraphe dans le guide utilisateur (FR + EN), qui nomme aussi le
  compromis : plus c'est juste, moins on voit large.

## Acceptance criteria

- [x] Une installation neuve démarre à 45°
- [x] Une installation existante qui a 90 stocké passe à 45 au démarrage
- [x] Une valeur autre que 90 est laissée telle quelle
- [x] Un 90 choisi **après** la migration survit à un redémarrage
- [x] Le marqueur est un réglage déclaré, comme celui de BL-125

## Ce qu'il ne fallait pas rater

**La migration doit pouvoir échouer au test.** Vérifié en la désactivant : le
test tombe (`'90' == '45'`). Un test de migration qui passe quoi qu'il arrive ne
prouve rien.

**Un 90 délibéré n'est pas impossible, seulement invraisemblable** — aucune
lunette XR ne présente 90° à un œil. D'où le marqueur : la migration ne passe
qu'une fois, et qui veut 90 le retape.
