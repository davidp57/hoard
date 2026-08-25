# Lot DL-RETRY — Relancer un téléchargement depuis l'historique

Status: ✅ done
Branch: feature/download-retry → PR → develop

## Problem Statement

L'historique de téléchargement (BL-075) conserve l'URL de tout ce qui est passé,
y compris des entrées **en échec, annulées ou interrompues**. Jusqu'ici il n'y
avait aucun moyen de les relancer : l'URL était visible dans l'infobulle du nom,
mais ni cliquable ni copiable, et la bookmarklet ne pouvait pas être rejouée sans
retourner sur la page d'origine.

C'est précisément le besoin né des pertes silencieuses corrigées par DL-INTEGRITY :
les vidéos perdues ne sont pas récupérables (elles n'ont jamais été écrites), mais
**leur URL, elle, est toujours dans l'historique**.

## Solution

Un bouton **↻** sur chaque entrée d'historique, qui remet la même URL dans la file
en réutilisant exactement le chemin d'un téléchargement normal.

## User Stories

1. En tant qu'utilisateur, je veux relancer un téléchargement échoué d'un clic,
   pour rattraper une vidéo perdue sans retrouver la page d'origine.
2. En tant qu'utilisateur, je veux être prévenu si je relance quelque chose qui a
   déjà réussi, pour ne pas créer un doublon par mégarde.

## Implementation Decisions

- **Le `referer` est désormais persisté** (migration `ALTER TABLE downloads`).
  Sans lui, relancer une URL de CDN direct — le cas le plus fréquent, puisque la
  bookmarklet envoie la source vidéo et la page en referer — serait rejeté sur les
  contrôles d'origine. Le bouton aurait été décoratif dans son cas d'usage principal.
- **Les cookies ne sont volontairement pas stockés** : ce sont des identifiants de
  session. Un site authentifié s'appuie sur le réglage `download_cookies_path`
  (fichier `cookies.txt` persistant). À dire explicitement dans la doc plutôt que
  de laisser croire à une relance universelle.
- **Endpoint dédié** `POST /api/downloads/{id}/retry` plutôt qu'un rappel de
  `/api/download` côté client : le backend lit l'URL, le titre et le referer depuis
  la ligne, journalise le lien avec l'entrée d'origine, et le client n'a rien à
  reconstruire.
- **`_queue_download()` factorisé** depuis `start_download` : la relance passe par
  la même validation SSRF, la même destination et la même file séquentielle. Une
  entrée d'historique n'est pas un laissez-passer — l'URL est **revalidée**
  (couvert par un test).
- **Chaque relance est une nouvelle entrée d'historique**, pas une mise à jour de
  l'ancienne : la trace de l'échec initial est conservée.
- **Confirmation seulement sur une entrée réussie** : la relance produit alors un
  second fichier suffixé ` (2)`, ce qui doit être annoncé et non subi.

## Testing Decisions

- Le cas qui justifie la fonctionnalité : une entrée en échec relancée aboutit.
- La conservation du `referer` est testée explicitement — c'est le point qui
  décide si le bouton sert à quelque chose.
- La revalidation de l'URL est testée avec une adresse locale (garde SSRF).

## Out of Scope

- Rejouer les cookies de la session d'origine (non stockés, et à raison).
- Relance automatique des entrées `interrupted` au démarrage : on trace, on ne
  décide pas à la place de l'utilisateur.

## Déjà livré dans ce lot

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-084 | Relancer un téléchargement depuis l'historique | feat | ✅ done |
