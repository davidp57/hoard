# BL-149 — Les infos de Stash dans Hoard, la progression dans Stash

Status: ✅ done
Lot: [FEAT-STASH](../PRD.md)

## Quoi

Décisions 5 et 6 du PRD, pour les seules vidéos de `stash_folder`.

## Critères d'acceptation

- [x] Liste : vignette de Stash, note, studio et performers ; une requête `findScenes` par dossier affiché, cache de quelques minutes ; Stash injoignable = liste normale, sans erreur bloquante.
- [x] Lecteur web : vignettes au survol de la barre de lecture (`vtt/thumbs` + sprite) et markers en chapitres sur la barre.
- [x] HereSphere : `thumbnailImage`, `thumbnailVideo`, tags préfixés (`Performer:`, `Studio:`, `Tag:`), markers en tags horodatés, note, `scripts` quand la scène a un funscript ; URL de médias signées.
- [x] Progression recopiée dans Stash depuis le point unique d'écriture de `progress` (lecteur web, suivi FPX, événements HereSphere) : au plus une requête toutes les 30 s par vidéo, plus pause et fermeture ; `sceneAddPlay` au passage « vu ». Un échec ne bloque jamais l'écriture dans Hoard.
- [x] Hors du dossier de Stash : aucune requête vers Stash, rien ne change.
- [x] Tests pytest avec le faux Stash : enrichissement de la liste et de HereSphere, limitation des envois de progression, passage « vu », Stash injoignable.
- [x] Doc : guide utilisateur FR + EN ; doc développeur.
