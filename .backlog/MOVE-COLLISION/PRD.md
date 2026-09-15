# Lot MOVE-COLLISION — Déplacer vers une destination occupée

Status: ✅ done
Branch: fix/move-collision → PR → develop

## Problem Statement

Déplacer certaines vidéos plantait le serveur, sans le moindre retour dans l'interface :

```
File "/app/backend/main.py", line 782, in _run_move
    conn.execute("UPDATE progress SET path = ? WHERE path = ?", (new_rel, old_rel))
sqlite3.IntegrityError: UNIQUE constraint failed: progress.path
```

`_run_move` réécrivait le chemin de la ligne `progress` vers la destination sans
vérifier qu'une ligne y était déjà — or `progress.path` est `PRIMARY KEY`. Deux
façons d'en arriver là : un fichier du même nom est déjà présent à destination et
porte une progression, ou une ligne **orpheline** est restée d'un fichier retiré
hors de Hoard, directement sur le NAS.

L'exception partait dans le thread du job, **non attrapée** : le job restait
`running` indéfiniment et l'interface attendait un déplacement qui n'arriverait
jamais. La base, elle, restait intacte (pas de `commit`).

Le plantage était en réalité un **garde-fou accidentel**. Rien ne vérifiait que la
destination était libre : sous Linux, `shutil.move()` passe par `os.rename()` et
**écrase silencieusement**. Déplacer une vidéo vers un dossier contenant déjà ce nom
détruisait donc la copie qui s'y trouvait — sans un mot — dès que l'ancien fichier
n'avait pas de ligne `progress` pour faire échouer la requête avant.

Trois défauts voisins sont apparus en instruisant celui-là : le déplacement d'un
**dossier** ne réécrivait que son propre chemin, perdant la progression de tout son
contenu ; la table `file_tags` n'était migrée nulle part (ni déplacement, ni
renommage) et jamais purgée à la suppression ; et le curseur manette générique posé
par BL-088 n'avait **aucun style**, donc il était invisible dans huit dialogues.

## Solution

Le serveur refuse une destination occupée en **409** et rend de quoi décider ;
l'interface ouvre une fenêtre **Écraser / Annuler**, utilisable à la manette comme au
clavier. L'écrasement est explicite, jamais implicite.

## User Stories

1. En tant qu'utilisateur, quand je déplace un fichier vers un dossier qui contient
   déjà ce nom, je veux qu'on me le dise et qu'on me laisse choisir d'écraser ou
   d'annuler — plutôt qu'un déplacement qui ne se termine jamais, ou une copie
   détruite sans avertissement.
2. En tant qu'utilisateur à la manette, je veux voir où est le curseur dans cette
   fenêtre et pouvoir répondre sans toucher l'écran.
3. En tant qu'utilisateur, je veux qu'un dossier déplacé emporte la progression et
   les tags de tout son contenu.

## Implementation Decisions

- **Le refus est synchrone, le déplacement reste un job.** Le client a besoin de la
  réponse tout de suite pour poser la question ; l'endpoint calcule donc la
  destination réelle (`move_target()`, partagée avec le job) et répond 409 avant de
  lancer le thread. Le job revérifie de son côté : il tourne plus tard, un fichier a
  pu apparaître entre-temps.
- **Le détail du 409 est structuré** (`{code, name, overwritable}`) plutôt qu'une
  phrase à analyser côté client. `overwritable` est faux dès que la source ou la
  destination est un dossier : déplacer un dossier sur un dossier l'imbriquerait
  dedans au lieu de le remplacer, ce qui n'est pas ce que « écraser » veut dire.
- **Le fichier remplacé est mis de côté, pas supprimé.** Il est renommé en
  `.<nom>.hoard-replaced-<hex>` dans le même dossier — donc jamais entre volumes —
  puis effacé une fois le déplacement réussi, ou remis en place s'il échoue. Un
  écrasement raté ne coûte rien. `os.replace()` aurait été atomique mais échoue entre
  systèmes de fichiers, et supprimer d'abord aurait perdu la victime sur un échec.
- **Les lignes orphelines sont purgées, pas contournées.** Après le garde-fou, une
  ligne restée à la destination ne peut plus être qu'orpheline : `_purge_paths()` la
  supprime dans la même transaction que la migration.
- **Le curseur manette démarre sur « Annuler ».** Écraser est définitif ; ça doit
  être choisi, pas atteint en appuyant sur A sur ce qui se trouvait sous le curseur.
- **La fenêtre ne porte aucun code manette à elle.** `gp-modal` +
  `data-gp-close` sur l'overlay suffisent : le parcours générique de BL-088 fait le
  reste, clavier compris.
- **Le style du curseur générique est corrigé à la racine** plutôt que ciblé sur la
  nouvelle fenêtre : les huit dialogues sans gestionnaire dédié étaient logés à la
  même enseigne.

## Testing Decisions

- Le cas signalé est testé tel quel : une ligne `progress` orpheline à la destination,
  aucun fichier — le déplacement doit réussir et la progression suivre.
- L'écrasement vérifie les trois effets ensemble : le contenu du fichier à
  destination, la progression qui devient celle du fichier déplacé, et l'absence de
  résidu de la copie mise de côté.
- Le job en échec est testé pour ce qu'il doit **rendre** (`status: error`), pas pour
  la façon dont il échoue : c'est le blocage de l'interface qui était le défaut.

## Out of Scope

- Un renommage automatique de type `nom (2).mkv` : c'est à l'utilisateur de décider
  quoi faire du doublon.
- Un écrasement de dossier par fusion récursive.
- Le même choix pour l'export de segments : le déplacement post-export refuse
  simplement une destination occupée et le signale dans le job.

## Tickets

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-090 | Destination occupée : choix écraser / annuler | fix | ✅ done |
| BL-091 | Métadonnées des dossiers : descendants et tags | fix | ✅ done |
| BL-092 | Un job de déplacement en échec doit se signaler | fix | ✅ done |
| BL-093 | Curseur manette générique invisible | fix | ✅ done |
