# BL-105 — Le contrôle de santé survit à l'authentification

Status: ✅ done
Type: fix
Parent: SEC-AUTH ([PRD](../PRD.md))
Files: `backend/main.py`, `Dockerfile`, `tests/test_api.py`

## What to build

Le `HEALTHCHECK` du Dockerfile interroge `http://localhost:8000/api/files?path=`,
une route protégée, **sans identifiants**. Dès qu'on active l'authentification, il
prend `401`, `urlopen` lève, `exit 1` — toutes les 30 s, 3 essais, et le container
passe `unhealthy`. Ce n'est pas propre à cette installation : activer
l'authentification cassait la surveillance de santé de n'importe quel déploiement.

Nouvelle route **`/healthz`**, exemptée du middleware d'authentification, sur
laquelle pointe le `HEALTHCHECK`.

Deux décisions de conception :

- **Exemption par égalité stricte**, pas par préfixe. Un test de préfixe aurait
  laissé passer `/healthz-nimportequoi` devant le garde.
- **La sonde vérifie vraiment quelque chose.** Elle interroge la base et
  contrôle que la racine média est un dossier, parce que l'ancienne sonde
  (`/api/files`) attrapait de fait une base cassée ou un montage disparu :
  renvoyer une constante aurait perdu cette couverture sans le dire.
- **Elle ne divulgue rien d'autre.** C'est la seule route accessible sans
  identifiants : pas de version, pas de chemin, pas de compteur — `{"status":
  "ok"}`, ou `503` avec `{"status": "error"}`.

## Acceptance criteria

- [x] `/healthz` répond `200` alors que l'authentification est active et que
      `/api/settings` répond `401`
- [x] Le corps est exactement `{"status": "ok"}`
- [x] `/healthzz`, `/healthz-oops` et `/healthz/sub` reçoivent `401` du
      middleware — la requête n'atteint jamais le routage
- [x] `/healthz` répond `503` quand la racine média a disparu
- [x] Le `HEALTHCHECK` du Dockerfile pointe sur `/healthz`
