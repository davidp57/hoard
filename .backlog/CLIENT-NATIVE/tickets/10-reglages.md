# BL-115 — Réglages et verrou PIN

Status: ⬜ ready
Type: feat
Parent: CLIENT-NATIVE ([PRD](../PRD.md))
Depends: 06
Files: `client/lib/`

## What to build

L'écran de réglages, adossé à `/api/settings` : dossier d'accueil, tri par
défaut, seuil de « vu », gestes, manette, transcodage.

**Le PIN doit être présenté pour ce qu'il est.** Il verrouille l'écran et rien
d'autre : aucune route ne le vérifie côté serveur, il ne protège pas l'accès à
l'API (voir lot SEC-AUTH). Ne pas laisser croire l'inverse dans l'interface.

L'authentification d'accès, elle, est du ressort du déploiement
(`HOARD_AUTH_USER` / `HOARD_AUTH_PASS`) et le client doit simplement savoir la
présenter.

## Acceptance criteria

- [ ] Parité avec l'écran de réglages web
- [ ] Le PIN verrouille l'écran du client
- [ ] Le libellé du PIN ne suggère pas une protection de l'API
