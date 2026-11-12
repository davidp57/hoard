# BL-137 — Toute l'interface en `rem`, une échelle à la racine

Status: ✅ done (reste l'essai sur le Frame)
Type: fix
Files: `frontend/index.html`, `docs/developer.*.md`, `docs/user-guide.*.md`, `CLAUDE.md`

## What was built

- `html { font-size: max(10px, min(100vw / 192, 100dvh / 108)) }` : 1rem = 10px
  jusqu'à 1920×1080, puis proportionnel au plus petit des deux rapports.
- `body` à `1.6rem` (les 16px par défaut sur lesquels la page a été dessinée).
- Conversion mécanique des ~850 tailles `px` > 2 en `rem` (÷10), dans le bloc
  `<style>` (hors commentaires et media queries) et dans les attributs `style="…"`.
- Restent en `px` : filets de 1-2px, seuils de media queries, bookmarklet (page
  d'un autre site), `rootMargin` d'`IntersectionObserver`.
- Fenêtres manette : `max(1.3rem, clamp(…vw…))` pour garder BL-126 en 3840×1080.

## Vérification (Chromium 152, fenêtre émulée)

| Taille | Mesure |
|---|---|
| 1280×800 | styles calculés des 821 éléments de la page identiques avant / après |
| 1920×1080 | racine 10px, en-tête 5,65 % de la hauteur |
| 3840×2160 | racine 20px, en-tête 5,60 % de la hauteur, pas de débordement |
| 3840×1080 | racine 10px, fenêtres manette 19,5px comme avant, côte à côte intact |

## Acceptance

- [x] Rien ne bouge en dessous de 1920×1080.
- [x] Taille apparente constante au-delà.
- [ ] Essai dans le Chromium du Steam Frame, fenêtré puis plein écran.
