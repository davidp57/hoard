# BL-122 — Réglages VR : champ de vision, convergence, sensibilité

Status: ✅ done
Type: feat
Files: `backend/main.py`, `frontend/index.html`, `tests/test_api.py`,
`docs/user-guide.*.md`

## Problem

BL-119 et BL-120 fixent en dur le champ de vision, la convergence et la sensibilité du
stick. Ces trois valeurs ne peuvent pas rester en dur : les studios ne cadrent pas
pareil d'un fichier à l'autre, et le confort n'est pas le même sur des lunettes XR que
sur un écran de laptop. Le projet range déjà ce genre de valeurs dans les réglages —
les constantes de gestes tactiles viennent de `cfg`, jamais du code.

## Dependencies

BL-119, BL-120.

## What to build

- Trois réglages ajoutés à `_SETTINGS_DEFAULTS` et au `POST /api/settings` :

| réglage | rôle | défaut |
|---|---|---|
| `vr_fov` | champ de vision horizontal de la vue rendue, en degrés | `90` |
| `vr_convergence` | écart de lacet entre les deux yeux en mode `sbs`, en degrés | `0` |
| `vr_look_speed` | vitesse de rotation au stick, en degrés par seconde à fond | `90` |
| `vr_sbs_layout` | `half` (lunettes XR, image réétirée) ou `full` | `half` |

- Une section **VR** dans la page Réglages, avec les bornes et une phrase disant ce
  que chaque valeur change à l'image.
- Le lecteur lit ces valeurs depuis `cfg`, jamais en dur — comme les constantes de
  gestes.
- Le champ de vision est aussi ajustable à chaud depuis le lecteur (zoom), sans
  écrire le réglage : un ajustement ponctuel n'est pas une préférence.

## Acceptance criteria

- [x] Les réglages ont une valeur par défaut, sont lus au démarrage et enregistrés
- [x] Un corps partiel envoyé à `POST /api/settings` laisse les autres réglages
      inchangés (comportement existant, testé)
- [x] Modifier `vr_fov` change le cadrage sans recharger la page — le lecteur lit
      `cfg` au moment de s'en servir au lieu de capturer la valeur au chargement
- [x] `vr_convergence` à zéro laisse les deux vues alignées (mesuré en BL-120)
- [x] Le zoom à chaud n'écrit pas le réglage
- [x] Les valeurs hors bornes sont refusées (422 sur six cas testés)
- [x] **Ajouté au périmètre** : `vr_sbs_layout`, né de BL-120. Validé à part contre
      son énumération — une valeur inconnue ferait calculer un rapport d'image faux
      sans que rien ne le signale.
