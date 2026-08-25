# BL-079 — Un téléchargement « terminé » doit avoir produit un fichier

Status: ✅ done
Type: fix
Files: `backend/main.py`, `tests/test_api.py`

## What to build

Supprimer la perte silencieuse de fichiers dans `_run_download`.

### Nom de sortie libre

- Helper `_unique_output_stem(output_dir, stem)` : renvoie `stem` s'il n'existe
  aucun fichier `stem.*` dans le dossier, sinon `stem (2)`, `stem (3)`… jusqu'à
  trouver libre (borne raisonnable, puis repli sur un suffixe unique).
- Comparaison par préfixe `stem + "."` via `iterdir()` — **pas** `glob()`, car un
  stem peut contenir `[`, métacaractère glob.
- Appliqué quand un `title` est fourni (cas de la bookmarklet et du formulaire).

### Échappement du template

- Les `%` du titre sont doublés (`%%`) avant d'entrer dans `outtmpl`, sinon yt-dlp
  interprète `%(...)` comme un champ. Vérifié : `Best of 50%(off) deal` produisait
  `Best of 50NAeal.mp4`.

### Détection du skip

- Compter les événements `downloading` dans le hook de progression. Zéro événement
  sur un job non annulé = yt-dlp a sauté le téléchargement (fichier déjà présent).
  Le job passe alors en `error` avec un message explicite, jamais en `done`.

### Nom réel et vérification finale

- Prendre `info["requested_downloads"][0]["filepath"]` comme source de vérité du
  fichier écrit ; repli sur `prepare_filename` si absent, **sans** forcer
  l'extension de `merge_output_format`.
- Avant de passer le job en `done` : vérifier que le fichier existe sur le disque.
  Sinon → `error` (« le fichier n'a pas été écrit »).
- Journaliser le chemin absolu et la taille du fichier produit (aujourd'hui seule
  l'URL est journalisée).

## Acceptance criteria

- [x] Deux téléchargements de contenus différents avec le même titre produisent deux fichiers distincts
- [x] Un skip de yt-dlp met le job en `error` avec un message explicite, jamais `done`
- [x] Un fichier final absent met le job en `error`
- [x] Le nom stocké dans l'historique est celui du fichier réellement écrit, extension comprise
- [x] Un titre contenant `%` produit un nom de fichier contenant ce `%`
- [x] `download completed` journalise le chemin absolu et la taille
- [x] Tests de non-régression sur les quatre points ci-dessus, sans accès réseau
- [x] `ruff check` + `ruff format --check` + `pytest` au vert

## Blocked by

None — can start immediately
