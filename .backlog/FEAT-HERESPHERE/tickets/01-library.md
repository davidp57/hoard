# BL-142 — Bibliothèque, scan et scènes HereSphere

Status: 🧑 waiting-human
Lot: [FEAT-HERESPHERE](../PRD.md)

## Quoi

Les routes `POST /heresphere`, `POST /heresphere/scan` et `POST /heresphere/scene/<id>`, au format relevé dans le PRD, avec les groupes et le format VR des décisions 3 à 5.

## Critères d'acceptation

- [x] `POST /heresphere` rend `access: 1` et les groupes « En cours », « Récemment vus », « Non vus », puis un groupe par dossier rapide ; chaque scène y figure par son URL `/heresphere/scene/<id>`, relative à la racine (voir *Réalisation*).
- [x] `POST /heresphere/scan` rend le détail de toutes les scènes listées (titre, durée quand elle est connue, date d'ajout).
- [x] `POST /heresphere/scene/<id>` rend titre, durée en ms, `projection` / `stereo` / `fov` selon `vr_modes` ou la détection par le nom, et une source média qui pointe sur `/api/file`.
- [x] Un identifiant qui sort de `MEDIA_ROOT`, ou qui ne désigne pas une vidéo, donne 404 (passe par `safe_path()`).
- [x] Sans identifiants, une requête est refusée comme le reste de l'API ; avec HTTP Basic, elle passe. Pas de régression sur le refus des écritures cross-site pour le navigateur.
- [x] Tests pytest sur le format des trois réponses, l'encodage des identifiants et le refus hors racine.
- [x] Doc : section « FramePlayerX / HereSphere » dans le guide utilisateur (FR + EN), qui dit quelle URL saisir dans FPX et avec quel compte ; routes dans la doc développeur.
- [ ] **Essai sur le Frame** : FPX › Sources › Add source › HereSphere avec l'URL de Hoard, groupes visibles, une vidéo 180° SBS et une vidéo plate lues dans le bon format (David).

## Réalisation (2026-11-14)

- Les URLs (scènes, média, `eventServer`) sont **relatives à la racine** plutôt qu'absolues : FramePlayerX les résout contre l'URL saisie (`resolve(base, …)`, couvert par ses propres tests). Derrière le reverse proxy Synology, le backend reçoit du HTTP simple et ne connaît ni le schéma ni l'hôte du client : une URL absolue construite côté serveur pourrait envoyer le casque sur `http://` ou sur le mauvais hôte.
- Format VR : en plus du mode réglé et du nom, la forme 2:1 (même règle que le lecteur web), lue par un ffprobe mis en cache — elle reconnaît 8 des 23 fichiers VR de l'échantillon de BL-121 que le nom rate. Le scan ne lance jamais ffprobe.
- Vérifié en HTTP réel (uvicorn, authentification activée, vrais fichiers et vrai ffprobe) : 401 sans identifiants, 200 en Basic sans `Sec-Fetch-*` sur les quatre routes, 403 conservé pour une écriture cross-site d'un navigateur.
