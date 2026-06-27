# Lot ALT-READERS — Lecteurs alternatifs : images, archives, PDF, audio ✅

Status: ✅ done
Terminé: 2026-05-15

**Goal**: Étendre Hoard aux médias non-vidéo. `#player-panel` accueille 4 sous-panels
(vidéo, images, PDF, audio). PDF.js bundlé localement, archives `.cbz` (ZIP stdlib) +
`.cbr` (rarfile + unrar). Dépendances : BL-054/055/056/057 dépendent de BL-053, BL-058 de tout.

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-053 | Backend socle (`media_type`, `/api/file`, archives, CBR) | feat | ✅ |
| BL-054 | Visionneuse images (dossier + standalone, modes zoom) | feat | ✅ |
| BL-055 | Archives (`.zip` / `.cbz` / `.cbr`) | feat | ✅ |
| BL-056 | Lecteur PDF (PDF.js, keyboard/gamepad, progress) | feat | ✅ |
| BL-057 | Lecteur audio (natif, UI dédiée) | feat | ✅ |
| BL-058 | Tests + intégration | chore | ✅ |
