# BL-116 — Empaquetage : Flatpak x86_64, Windows, CI

Status: ⬜ ready
Type: chore
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 04
Files: `client/`, `.github/workflows/`

## What to build

Passer du montage jetable de BL-104 à un paquet qu'on installe.

**Ce que le spike a appris, et qui décide de la forme du paquet.** `media_kit`
ne livre pas de libmpv pour Linux : son plugin vidéo réclame `libmpv.so.2` avec
un `RUNPATH` figé sur la machine de compilation, si bien qu'ailleurs le
chargement se rabat en silence sur la libmpv du système — et échoue quand il
n'y en a pas. `LIBMPV_LIBRARY_PATH`, que `media_kit` documente pour ça, **ne
peut pas corriger** le problème : elle est lue par le code Dart, bien après le
refus de l'éditeur de liens.

Le montage de test contourne ça en embarquant les bibliothèques absentes de
SteamOS et en posant `LD_LIBRARY_PATH` au lancement. Ça marche, mais la liste
est mesurée sur **une** version de SteamOS et vieillira : elle a déjà été
fausse une fois, avec un conflit `libmount` / `libgio` qui empêchait tout
démarrage.

Le **Flatpak** est la réponse durable : un runtime cohérent, libmpv sur un
chemin standard du bac à sable, et plus aucune liste à tenir à jour. C'est
aussi la seule voie propre sur SteamOS, dont le système est en lecture seule.

À produire : Flatpak x86_64, build Windows, et la CI qui fabrique les deux.
Prévoir que la CI passe de quelques secondes à plusieurs minutes.

## Acceptance criteria

- [ ] Flatpak x86_64 installable sur SteamOS, sans dépendance système
- [ ] `client/tools/steamos-missing-libs.txt` et son lanceur retirés, devenus
      inutiles — ou clairement marqués comme outillage de test seulement
- [ ] Build Windows
- [ ] CI produisant les artefacts
