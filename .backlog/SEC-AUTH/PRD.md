# Lot SEC-AUTH — Une instance ouverte doit se voir

Status: 🔄 in-progress
Branch: `feature/client-native` (livré avec le lot CLIENT-NATIVE)

## Problem Statement

Le 2026-09-21, en préparant le client natif, on a constaté que l'instance de
production répondait `200` depuis Internet **sans aucune authentification** —
vérifié sur `/api/settings` et `/api/files`. Or l'API expose aussi
`DELETE /api/files`, `POST /api/files/move`, `POST /api/download` (téléchargement
arbitraire sur le NAS), `POST /api/restart` et `POST /api/settings`. N'importe
qui connaissant l'adresse pouvait lister, télécharger, déplacer et **supprimer**.

Le mécanisme n'était pas en cause : l'authentification HTTP Basic (BL-011) est
correctement écrite — middleware global, comparaison à temps constant. Trois
défauts l'ont rendue inopérante et invisible :

1. **Elle s'éteint en silence.** `_AUTH_ENABLED` vaut `False` dès qu'une des deux
   variables manque, sans un mot dans les logs. Une instance ouverte est
   indiscernable d'une instance protégée, y compris pour son propriétaire.
2. **`docker-compose.yml` ne mentionnait pas les variables**, pas même en
   commentaire — alors qu'il documente le TLS. Rien, dans le fichier qu'on édite
   pour déployer, ne laissait deviner qu'il fallait les poser.
3. **La documentation les mentionne**, mais noyées dans un tableau de douze
   variables, sans dire que le défaut est « ouvert ».

Et une fois l'authentification activée, un quatrième défaut est apparu : le
`HEALTHCHECK` du Dockerfile interroge `/api/files?path=`, une route protégée,
**sans identifiants**. Il prend `401`, échoue toutes les 30 s, et le container
passe `unhealthy` — pour tout le monde, pas seulement ici.

Le **code PIN** n'a jamais couvert ce risque : il verrouille l'interface web, et
aucune route ne le vérifie. L'utilisateur pouvait raisonnablement croire le
contraire.

## Solution

Ne pas se contenter de fermer cette instance-là — faire qu'une instance ouverte
se voie, et qu'activer l'authentification ne casse rien.

- **Une route `/healthz` publique**, exemptée du middleware par une comparaison
  exacte, qui vérifie la base et la racine média sans rien divulguer d'autre
  qu'un `{"status": "ok"}`. Le `HEALTHCHECK` pointe dessus.
- **Un message à chaque démarrage** disant si l'authentification est active, et
  ce que « désactivée » implique concrètement.
- **Les variables dans `docker-compose.yml`**, commentées comme l'est le TLS,
  avec le piège des guillemets.
- **Une section dédiée dans la doc d'installation** (FR + EN), qui dit le défaut
  et corrige l'idée fausse sur le PIN.

## Hors périmètre

- **Un vrai système de comptes.** HTTP Basic suffit à un usage personnel ; un
  modèle multi-utilisateur est un autre sujet (BL-015, lot FEAT-ADVANCED).
- **Protéger les routes par le PIN.** Ce serait mélanger un verrou d'interface
  et une authentification ; le PIN reste ce qu'il est, la doc le dit désormais.
- **Forcer l'authentification par défaut.** Ça casserait toutes les instances
  existantes sur réseau local au prochain redémarrage. Le choix est de rendre
  l'état **visible**, pas de le changer sous les pieds des gens.

## Tickets

| # | Ticket | Status |
|---|---|---|
| 01 | BL-105 — Le contrôle de santé survit à l'authentification | ✅ |
| 02 | BL-106 — Une instance ouverte l'annonce | ✅ |
