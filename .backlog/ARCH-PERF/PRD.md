# Lot ARCH-PERF — Architecture & Performance

Status: ⬜ ready
Branch: feature/arch-perf (ou une branche par ticket) → PR → develop

## Problem Statement

Dettes techniques ouvertes :

1. **`backend/main.py` a grossi** (~2 000+ lignes) et mélange setup DB, streaming,
   file d'attente yt-dlp et routes FastAPI. Navigation et revue deviennent pénibles.
2. **Transcodage logiciel uniquement** : le H.265→H.264 software est gourmand en CPU
   et peut saturer un NAS bas de gamme, alors que la plupart des SoC NAS exposent un
   encodeur matériel (VAAPI Intel, NVENC GPU).
3. **Coût de détection des galeries** (BL-074) : `/api/files` fait un `rglob`
   récursif par sous-dossier (voire deux pour les non-galeries). À optimiser si le
   listing rame sur de grosses arborescences. *Watch item — non urgent.*

## Solution

- **Découper `main.py`** en modules ciblés (`db.py`, `stream.py`, `download.py`,
  `config.py`) en gardant `main.py` comme point d'entrée FastAPI. Aucun changement
  de comportement ; tous les tests passent sans modification.
- **Transcodage matériel optionnel** via `FFMPEG_HW_ACCEL` (vide = software), 100 %
  opt-in, fallback software silencieux si le device est absent.

## User Stories

1. En tant que mainteneur, je veux un backend modulaire, pour naviguer et réviser le
   code sans parcourir un fichier monolithique.
2. En tant qu'hébergeur sur NAS bas de gamme, je veux activer l'encodage matériel,
   pour transcoder sans saturer le CPU.

## Implementation Decisions

- Découpage : globals partagés (`MEDIA_ROOT`, `FFMPEG_BIN`, `FFPROBE_BIN`) déplacés
  dans `backend/config.py` pour éviter les imports circulaires.
- HW : injecter les flags encodeur appropriés selon `FFMPEG_HW_ACCEL` ; documenter
  l'exposition de `/dev/dri` dans `docker-compose.yml` (Synology). Warning + fallback
  software si device indisponible au démarrage.
- Séquencement conseillé : faire le découpage (BL-041) avant le HW (BL-042) pour que
  les flags atterrissent dans `stream.py`.

## Testing Decisions

- BL-041 : aucun test modifié ne doit échouer (refactor sans changement de comportement).
- BL-042 : l'option matérielle ne doit jamais casser le chemin software par défaut.

## Out of Scope

- Architecture en couches / framework lourd — on reste sur des modules plats.
- Support GPU exotique au-delà de VAAPI/NVENC.

## Further Notes

Lockstep doc : `docs/developer.*.md` (architecture, env vars) + `CHANGELOG.md`.

## Déjà livré dans ce lot

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-067 | Cleanup — suppression de l'endpoint `/api/stream` mort | chore | ✅ done |
