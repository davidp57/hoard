# BL-082 — Le bouton « Parcourir… » ne fait rien

Status: ✅ done
Type: fix
Files: `frontend/index.html`

## Problème

Retour utilisateur immédiatement après la livraison de BL-080 : « le bouton
Parcourir ne fait rien ». Deux défauts cumulés, qui donnent le même symptôme.

### 1. Le sélecteur s'ouvre derrière la page des réglages

`dest-picker-overlay` porte `z-index: 300`, `#settings-page` porte `z-index: 500`.
Le sélecteur s'ouvrait donc correctement — invisible, sous la page qui l'avait
ouvert. Jusqu'ici il n'était appelé que depuis le modal de déplacement
(`z-index: 300`), où le problème ne se posait pas.

**Ce défaut aurait dû être vu à la livraison.** La vérification faite alors
lisait `overlay.style.display === 'flex'` dans le DOM, ce qui était vrai, sans
jamais contrôler ce qui était réellement peint à l'écran.

### 2. Même au premier plan, il s'ouvrirait vide

`openDestPickerForFolder()` démarre sur le dossier actuellement configuré. Quand
celui-ci n'existe pas — le cas exact d'une destination signalée « n'existe pas
encore » — `/api/files` répond **404** avec un corps JSON `{detail: "..."}`.

`_loadDestPickerDir()` faisait `.then(r => r.json())` sans regarder le statut :
l'objet d'erreur est *truthy*, donc le garde `if (!r)` ne se déclenchait pas, et
la ligne suivante (`r.entries.filter(...)`) levait une `TypeError` après que le
fil d'Ariane ait déjà été écrit. Résultat : ni liste, ni message d'erreur.

Ce défaut **préexistait** dans le sélecteur de déplacement de fichiers ; l'usage
introduit par BL-080 l'a simplement rendu atteignable.

## Correctif

- `dest-picker-overlay` passe en `z-index: 700`, au-dessus de `#settings-page`
  (500) comme du modal de déplacement (300), et sous rien d'autre qu'il doive
  masquer.
- `_loadDestPickerDir()` vérifie `resp.ok` **et** la présence de `entries`. Un
  chemin introuvable replie sur la racine avec un toast explicite au lieu
  d'échouer en silence ; à la racine, l'erreur est signalée normalement.

## Vérification

Reproduite dans la configuration exacte de l'utilisateur
(`download_folder = "[[_downloads"`, dossier absent) :

- le sélecteur est **réellement** au premier plan — contrôlé par
  `document.elementFromPoint()` au centre du modal, pas par le DOM ;
- il se replie sur la racine et liste les dossiers ;
- navigation sur deux niveaux puis validation : le champ et le chemin complet
  se mettent à jour.

## Acceptance criteria

- [x] Le sélecteur est visible au premier plan quand il est ouvert depuis les réglages
- [x] Un dossier de départ inexistant replie sur la racine avec un message
- [x] La navigation et la validation renseignent le champ et le chemin affiché
- [x] Le sélecteur de déplacement de fichiers bénéficie du même garde-fou
- [x] Vérification par le rendu réel, pas par l'état du DOM

## Blocked by

None
