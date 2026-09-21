# BL-106 — Une instance ouverte l'annonce

Status: ✅ done
Type: fix
Parent: SEC-AUTH ([PRD](../PRD.md))
Files: `backend/main.py`, `docker-compose.yml`, `docs/installation.en.md`, `docs/installation.fr.md`

## What to build

La cause racine de l'incident n'est pas que l'authentification était désactivée
— c'est un défaut défendable sur réseau local — mais qu'**on ne pouvait pas le
savoir**. `_AUTH_ENABLED` passe à `False` dès qu'une des deux variables manque,
sans un mot. Une instance publiée sur Internet et une instance protégée
produisent exactement les mêmes logs.

Trois corrections, toutes du même ordre : rendre l'état visible là où quelqu'un
le regardera.

1. **Au démarrage**, à côté de la ligne de version déjà affichée : soit
   `Auth: HTTP Basic enabled for user '<nom>'`, soit un message disant que tout
   est ouvert, **en nommant ce qui l'est** (suppression et déplacement de
   fichiers) plutôt qu'un « auth disabled » que l'œil saute. Doublé d'un
   `logger.warning` pour qu'il apparaisse dans le journal consultable depuis
   l'interface.
2. **Dans `docker-compose.yml`**, les deux variables en commentaire, comme l'est
   déjà le TLS — c'est le fichier qu'on édite pour déployer. Avec le piège des
   guillemets, qui transforme `HOARD_AUTH_PASS="abc"` en un mot de passe de cinq
   caractères.
3. **Dans la doc d'installation** (FR + EN), une section dédiée avant celle du
   HTTPS. Les variables y figuraient déjà, mais dans un tableau de douze lignes
   qui ne disait pas que le défaut est « ouvert ». La section corrige aussi
   l'idée fausse sur le code PIN, qui ne verrouille que l'interface.

**Ce qu'on ne fait pas : activer l'authentification par défaut.** Ça couperait
l'accès à toutes les instances sur réseau local au prochain redémarrage, sans
prévenir. Le but est que l'état soit lisible, pas qu'il change sous les pieds
des gens.

## Acceptance criteria

- [x] Le démarrage affiche l'état de l'authentification dans les deux cas
- [x] Le message « désactivée » nomme les conséquences concrètes
- [x] `logger.warning` émis quand l'authentification est désactivée
- [x] `docker-compose.yml` porte les deux variables commentées et l'avertissement
- [x] `docs/installation.en.md` et `.fr.md` ont une section « Authentification »
      qui dit le défaut, le piège des guillemets, l'obligation du HTTPS et le
      périmètre réel du PIN
