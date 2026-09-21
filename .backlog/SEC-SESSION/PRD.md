# Lot SEC-SESSION — Session par cookie et jeton pour la bookmarklet

Status: ⬜ ready
Branch: `feature/sec-session` (à créer)

## Problem Statement

L'authentification HTTP Basic (BL-011, rendue visible par BL-106) est **activée en
production depuis le 2026-09-21**. Elle protège correctement, et elle coûte trois
choses à l'usage :

1. **Les identifiants sont à ressaisir** à chaque nouvelle fenêtre de navigateur.
   Sur le Steam Deck et le Steam Frame, la fenêtre native du navigateur se pilote
   mal à la manette — c'est exactement le grief qui avait motivé le lot
   `CLIENT-NATIVE`, et il revient par une autre porte.
2. **La bookmarklet de téléchargement est cassée.** Elle poste vers Hoard depuis
   une page tierce, donc en *cross-origin* : le navigateur n'attache pas les
   identifiants Basic, et le CORS en `allow_origins=["*"]` interdit de le lui
   demander. À confirmer d'un essai, mais les deux conditions sont réunies dans le
   code (`backend/main.py:164` et `backend/main.py:226`).
3. **Il n'y a pas d'écran de connexion propre** : la fenêtre native du navigateur
   est le seul point d'entrée, et elle ne ressemble à rien du reste de l'interface.

Ce que ce lot **ne cherche pas** : la déconnexion. Elle a été proposée et écartée
par l'utilisateur. La route qui efface le cookie existera quand même, parce qu'un
cookie qu'on ne peut pas effacer est un défaut, mais ce n'est pas un objectif du
lot et elle n'a pas à être mise en avant dans l'interface.

## Solution

Deux mécanismes distincts, pour deux besoins qu'il ne faut pas confondre.

**Une session par cookie**, pour le navigateur. Un écran de connexion maison pose
un cookie signé, et le middleware l'accepte en plus de Basic.

**Un jeton dédié**, pour la bookmarklet. Un cookie correct est `SameSite=Lax` ou
`Strict` — c'est précisément ce qui empêche un site tiers de déclencher une action
chez soi — donc **il ne partira jamais depuis la bookmarklet**. Le cookie ne répare
pas la bookmarklet, et vouloir qu'il le fasse reviendrait à ouvrir la porte que
`SameSite` ferme.

## User Stories

1. En tant qu'utilisateur sur Deck ou Frame, je veux me connecter une fois et ne
   plus y revenir, pour ne pas affronter la fenêtre native du navigateur à la
   manette.
2. En tant qu'utilisateur, je veux un écran de connexion qui ressemble à Hoard et
   se pilote comme le reste, manette comprise.
3. En tant qu'utilisateur, je veux que la bookmarklet remarche malgré
   l'authentification activée.

## Implementation Decisions

Ces choix sont **proposés et recommandés**, pas encore confirmés — le premier
geste du lot est de les faire valider (voir *Points à confirmer*).

- **Cookie signé, sans table de sessions.** HMAC sur `{utilisateur, expiration}`.
  Pas de table à maintenir, et la rotation de la clé révoque tout d'un coup.
- **La clé de signature vient d'une variable d'environnement**, avec repli sur une
  clé générée au premier démarrage et rangée dans `settings`. Sans variable, ça
  marche tout seul ; avec, on peut invalider toutes les sessions en la changeant.
- **Le middleware accepte cookie *ou* Basic.** Retirer Basic casserait `curl`, un
  futur client natif et tout lecteur externe. Les deux coexistent.
- **`WWW-Authenticate` n'est plus envoyé aux navigateurs.** Tant qu'il y est, le
  navigateur ouvre sa propre fenêtre et l'écran de connexion ne s'affiche jamais.
  Il reste envoyé aux requêtes non-HTML, pour que `curl -u` continue de marcher.
- **Le jeton de la bookmarklet voyage dans le corps de la requête, jamais dans
  l'URL** : un jeton d'authentification dans une URL finit dans les journaux du
  reverse proxy. Le POST est déjà en JSON, donc rien à changer au CORS.
- **Le jeton n'ouvre que `/api/download`.** Il circule dans un marque-page, sur des
  sites tiers : il ne doit pas pouvoir supprimer un fichier.
- **Le CORS reste en `allow_origins=["*"]`.** Ce n'est pas une faille en soi — avec
  `*` le navigateur refuse justement les requêtes authentifiées — et on ne durcit
  pas un réglage pareil en passant. À traiter séparément si le besoin apparaît.

## Découpage

| # | Ticket | Dépend de | Statut |
|---|---|---|---|
| 01 | [BL-123](tickets/01-session-cookie.md) — Écran de connexion et session par cookie | — | ⬜ |
| 02 | [BL-124](tickets/02-jeton-bookmarklet.md) — Jeton dédié pour la bookmarklet | — | ⬜ |

Les deux tickets sont indépendants. BL-124 est le plus urgent à l'usage, puisque
la bookmarklet est cassée **maintenant**.

## Points à confirmer en ouverture de lot

1. Supprimer la fenêtre native du navigateur pour les requêtes HTML — sans ça
   l'écran de connexion ne sert à rien. Recommandé : oui.
2. Durée de session de 30 jours, renouvelée à l'usage. Recommandé : oui.
3. Clé de signature : variable d'environnement prioritaire, repli sur une clé
   générée en base. Recommandé : les deux.
4. Un seul lot, deux tickets, une PR. Recommandé : oui.

## Hors périmètre

- **La déconnexion comme fonctionnalité** — écartée par l'utilisateur (la route
  existera, l'interface n'en fera pas un argument).
- **Resserrer le CORS** — voir ci-dessus.
- **Remplacer le verrou PIN** — c'est un verrou d'écran, pas une authentification
  serveur ; les deux restent distincts.
- **OAuth, comptes multiples, rôles** — le multi-utilisateur est le sujet de
  BL-015, dans `FEAT-ADVANCED`.
