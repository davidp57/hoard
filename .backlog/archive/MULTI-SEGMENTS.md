# Lot MULTI-SEGMENTS — Sélection multi-zones et export ✅

Status: ✅ done
Terminé: 2026-05-15

**Goal**: Remplacer la découpe IN/OUT unique par un système multi-segments ; segments
stockés en SQLite ; export individuel ou fusionné via FFmpeg (concat lossless) ; support
clavier et gamepad complet.

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-047 | Table `segments` (id, path, seg_in, seg_out) + endpoints CRUD | feat | ✅ |
| BL-048 | Export backend : mode `individual` + mode `merged` (concat demuxer) | feat | ✅ |
| BL-049 | UI seekbar : marqueurs IN/OUT, fills par segment, chips | feat | ✅ |
| BL-050 | Modal export (`individual`/`merged`, conserver original, gamepad 2 phases) | feat | ✅ |
| BL-051 | Tests CRUD segments, export, range invalide ; migration `init_db()` | chore | ✅ |
