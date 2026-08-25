# BL-083 — La suite de tests atteint le vrai yt-dlp et part sur le réseau

Status: ✅ done
Type: fix
Files: `tests/conftest.py`, `tests/test_api.py`, `backend/main.py`

## Problème

La suite se figeait **une fois sur deux** en local (de 8 s à plus de 5 minutes),
et l'étape « Run tests » de la CI restait bloquée trois fois de suite sur les
releases v2.5.0, v2.5.1 et v2.5.2 — attribué à tort à des **runners GitHub
défaillants**, jusqu'à ce qu'une capture de pile tranche.

Pile obtenue avec `-o faulthandler_timeout=40` :

```
start_download → _prepare_download → sync_enqueue → _run_download → _extract
  → yt_dlp.YoutubeDL.extract_info → curl_cffi.session.request → réseau
```

Le **vrai** yt-dlp était utilisé, et émettait une vraie requête HTTP **sans
timeout**, qui pend indéfiniment.

### Pourquoi le mock ne protégeait pas

Chaque test remplace `sys.modules["yt_dlp"]` par un double, mais `monkeypatch`
restaure l'entrée à la fin du test — **pendant que les threads de téléchargement
lancés par ce test peuvent encore tourner**. Le thread retardataire (worker
`dl-worker` ou thread de préparation) exécute alors `import yt_dlp` et récupère
le module authentique.

`requirements-dev.txt` inclut `backend/requirements.txt` : yt-dlp et curl-cffi
sont donc réellement installés dans l'environnement de test. Le piège était armé
bien avant ce lot ; les nouveaux tests de téléchargement n'ont fait qu'augmenter
la probabilité de le déclencher.

Test observé au moment du blocage : `test_download_done_after_sync_thread` — mais
il mocke correctement : il hérite du thread d'un test précédent. Corriger un test
en particulier n'aurait donc rien réglé.

## Correctif

1. **Fixture `autouse` de session** (`_forbid_real_yt_dlp`) : `sys.modules["yt_dlp"]`
   reçoit un substitut dont `YoutubeDL()` lève une `RuntimeError` explicite.
   Un thread retardataire **échoue bruyamment** au lieu de pendre, et
   `monkeypatch` restaure vers ce substitut, jamais vers le vrai module.
2. **`socket_timeout` en production** : aucun timeout réseau n'était transmis à
   yt-dlp. Un hôte qui accepte la connexion puis se tait immobilisait le worker,
   et la file étant séquentielle, tout s'accumulait derrière. Réglable par
   `DOWNLOAD_SOCKET_TIMEOUT` (défaut 30 s).

## Acceptance criteria

- [x] Le vrai yt-dlp est inatteignable depuis la suite, et le prouver est testé
- [x] Un thread dont le patch a expiré produit une erreur explicite, pas un blocage
- [x] `socket_timeout` est transmis à yt-dlp et couvert par un test
- [x] Quatre exécutions consécutives de la suite passent en 8–12 s (avant : une sur deux se figeait)
- [x] `ruff check` + `ruff format --check` + `pytest` au vert

## Blocked by

None
