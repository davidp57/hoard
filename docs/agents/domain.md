# Docs de domaine

Repo single-context.

- Contexte produit / architecture : `CLAUDE.md` (contexte projet, français) et
  `.github/copilot-instructions.md` (conventions, workflows, architecture).
- Décisions d'architecture : `docs/adr/`.
- Pas de `CONTEXT.md`/glossaire dédié à ce jour : le vocabulaire métier vit dans
  `CLAUDE.md` et les docs developer (`docs/developer.*.md`).

Les skills qui lisent le contexte de domaine (`improve-codebase-architecture`,
`diagnose`, `tdd`) doivent lire `CLAUDE.md` et consulter `docs/adr/` pour les
décisions antérieures dans la zone modifiée.
