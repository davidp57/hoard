# Lot OPS-VISIBILITY — Traçabilité & exploitation

Status: ✅ done
Branch: feature/ops-visibility → PR → develop

## Problem Statement

Hoard tourne en container sur le NAS, sans aucune trace durable de ce qu'il fait.
Trois angles morts, constatés à l'usage :

1. **Aucun historique de téléchargement.** Les jobs vivent dans le dict en mémoire
   `_jobs` (`backend/main.py`), sont purgés 1 h après leur fin (`JOB_TTL_SECONDS`) et
   disparaissent à chaque redémarrage du container. Un téléchargement lancé via la
   bookmarklet qui échoue ne laisse **rien** : impossible de distinguer « ça a raté »
   de « ça n'a jamais été lancé ». C'est exactement le symptôme rencontré — des
   ajouts introuvables, sans moyen de savoir ce qui s'est passé.
2. **Aucune rétention de logs.** `logging.basicConfig()` écrit sur stdout ; seul le
   driver de logs Docker les capture, et les anciens ne sont pas conservés. Quand on
   veut enquêter, la trace a déjà disparu.
3. **Aucun moyen de redémarrer l'application** autrement qu'en passant par Portainer
   (ou SSH) sur le NAS. Après un changement de réglage bas niveau ou un worker de
   téléchargement coincé, c'est le seul recours.

## Solution

- **Persister les jobs de téléchargement en SQLite** (table `downloads`) et exposer
  une **vue historique** dans l'UI, avec le statut final et le message d'erreur.
- **Journaliser dans un fichier rotatif** sur le volume persistant, avec une
  rétention de **30 jours**, et rendre les logs consultables depuis l'UI.
- **Ajouter un bouton « Redémarrer Hoard »** dans les réglages, qui termine le
  process et laisse le superviseur du container le relancer.

## User Stories

1. En tant qu'utilisateur, je veux retrouver la liste de ce que j'ai téléchargé et
   savoir ce qui a échoué, pour ne plus chercher un fichier qui n'existe pas.
2. En tant qu'utilisateur, je veux consulter les logs des derniers jours depuis
   l'interface, pour diagnostiquer sans ouvrir Portainer.
3. En tant qu'utilisateur, je veux redémarrer Hoard depuis les réglages, pour
   débloquer l'application sans passer par le NAS.

## Implementation Decisions

- **Portée de la persistance** : uniquement les jobs de type `download`. Les jobs
  `cut` / `export` restent volatils (ils sont déclenchés depuis l'UI, avec un retour
  immédiat — le besoin de traçabilité ne s'y pose pas).
- **`_jobs` reste le store chaud.** La DB est un miroir en écriture seule depuis les
  workers : chaque transition d'état fait un upsert. Aucun changement du
  comportement temps réel (`/api/jobs` inchangé, polling identique).
- **Jobs interrompus** : au démarrage, toute ligne `downloads` non terminale
  (`pending` / `resolving` / `running`) est repassée en `interrupted` — le container
  a redémarré au milieu. Sans ça l'historique afficherait des téléchargements
  éternellement « en cours ».
- **Rétentions distinctes** : les **logs** sont volumineux → 30 jours par défaut.
  L'**historique de téléchargement** pèse quelques centaines d'octets par ligne, et
  son intérêt est précisément de retrouver un ajout ancien → **illimité par défaut**,
  bornable via un réglage.
- **Logs fichier** dans un sous-dossier du volume qui porte déjà la DB
  (`<DB_PATH.parent>/logs`), donc persistant sans toucher au `docker-compose.yml`
  existant. stdout est conservé en parallèle (Portainer continue de fonctionner).
- **Redémarrage** : `POST /api/restart` répond d'abord, puis termine le process. Le
  relancement est la responsabilité du superviseur (`restart: unless-stopped` dans
  `docker-compose.yml`). Hors container, le bouton arrête l'application — à
  documenter explicitement.
- **Sécurité** : Hoard dispose d'une authentification HTTP Basic **optionnelle**
  (`HOARD_AUTH_USER` / `HOARD_AUTH_PASS`, BL-011) appliquée par un middleware global :
  les nouveaux endpoints en héritent automatiquement. Le PIN, lui, n'est qu'un verrou
  d'interface. Sans Basic auth activée, `/api/restart` et `/api/logs` sont donc aussi
  joignables que `/api/delete`, déjà destructif — pas de régression du modèle de
  menace, mais `/api/logs` élargit un peu la surface d'exposition (URLs et IP
  clientes journalisées). À mentionner dans la doc d'installation.

## Testing Decisions

- Les tests existants sur `/api/jobs` et `/api/download` ne doivent pas changer.
- Nouveaux tests : écriture en DB au fil des transitions, requalification en
  `interrupted` au démarrage, purge au-delà de la rétention, endpoint de lecture de
  l'historique et sa pagination.
- Les logs fichier sont désactivés dans les tests (`LOG_DIR=""`) pour ne rien écrire
  hors du répertoire temporaire de la fixture.
- `/api/restart` est testé sans tuer le process de test : la terminaison passe par
  une fonction indirecte, remplacée par un double dans le test.

## Out of Scope

- Authentification serveur (couverte par BL-015).
- Reprise automatique des téléchargements interrompus après redémarrage — on trace,
  on ne relance pas. Le relancement manuel depuis l'historique reste une évolution
  possible.
- Centralisation des logs (syslog, driver Docker externe).

## Further Notes

Lockstep doc : `docs/user-guide.*.md` (vue historique, bouton de redémarrage),
`docs/developer.en.md` (table `downloads`, variables d'environnement de log,
endpoint de redémarrage), `docs/installation.*.md` (rétention et emplacement des
logs), `CHANGELOG.md` + `docs/changelog-user.fr.md`.

## Déjà livré dans ce lot

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-075 | Persistance des téléchargements et vue historique | feat | ✅ done |
| BL-076 | Journalisation fichier avec rétention de 30 jours | feat | ✅ done |
| BL-077 | Redémarrer Hoard depuis l'interface | feat | ✅ done |
| BL-078 | Worker de téléchargement tué par une exception inattendue | fix | ✅ done |
