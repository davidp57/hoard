# BL-129 — Convergence retenue par fichier

Status: ✅ done
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`,
`docs/user-guide.*.md`, `docs/developer.en.md`

## Problem

Une convergence réglée à la manette (BL-128) vit en mémoire et meurt à la
fermeture du lecteur : il faudrait refaire l'ajustement à chaque ouverture.

**Tranché par David le 2026-09-21 : retenue par fichier**, et non globalement.
La raison est que la gêne vient du **tournage** — un fichier monté avec un
écartement de caméras inhabituel — plus que des yeux de l'utilisateur. Un fichier
mal monté ne doit donc pas contaminer les autres.

## What to build

Le mode VR est déjà retenu par fichier depuis BL-121, table `vr_modes(path, mode,
updated_at)`. **Ajouter une colonne** plutôt qu'une table : c'est la même clé, le
même cycle de vie, et les mêmes règles de suivi.

- `ALTER TABLE vr_modes ADD COLUMN convergence REAL` dans `init_db()`, dans le
  style des migrations de schéma déjà présentes.
- **Le réglage global reste le défaut** (`cfg.vr_convergence`, Paramètres →
  Player) ; la valeur par fichier ne s'applique que si elle existe.
- **Seul un geste explicite écrit.** Même règle que BL-121 : la remise à zéro
  automatique d'une nouvelle source ne doit rien écraser.
- **La ligne suit les renommages et déplacements et disparaît avec le fichier** —
  c'est déjà le cas pour `vr_modes`, vérifier que la colonne suit et **le tester**,
  sans quoi un nouveau fichier déposé au même chemin hériterait de la convergence
  d'un inconnu. Les deux cas sont déjà testés pour `mode` : les étendre.

## Acceptance criteria

- [ ] Une convergence réglée à la manette est retrouvée à la réouverture du fichier
- [ ] Un autre fichier n'en hérite pas : il prend le défaut global
- [ ] Le réglage global continue de servir de défaut
- [ ] La ligne suit un renommage et un déplacement
- [ ] La ligne disparaît avec le fichier
- [ ] Une valeur hors bornes est refusée (±3°, comme `VR_CONVERGENCE_MAX`)

## Ce qu'il ne faut pas rater

`vr_modes` n'a de ligne que si un **mode** a été choisi : régler la convergence sur
un fichier dont le mode n'a jamais été enregistré doit créer la ligne, pas échouer
silencieusement. Le `POST /api/vr-mode` actuel écrit `mode` en NOT NULL —
l'insertion depuis la convergence seule doit rester valide.
