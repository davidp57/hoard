# Lot SECURITY-QUALITY-UX — Sécurité, Qualité & UX ✅

Status: ✅ done
Terminé: 2026-06-14

**Goal**: Issu de la revue technique du 2026-05-09 (+ correctifs UX). Durcissement
sécurité, robustesse backend et accessibilité frontend. BL-011 (auth) débloque la
progression multi-utilisateur (lot `FEAT-ADVANCED`).

| ID | Titre | Type | Statut |
|----|-------|------|--------|
| BL-011 | Authentification HTTP Basic opt-in (`HOARD_AUTH_USER`/`PASS`) | feat | ✅ |
| BL-027 | Streaming — validation Range header (HTTP 416) sur `/api/file` | fix | ✅ |
| BL-028 | `safe_path()` — bloquer les symlinks échappant `MEDIA_ROOT` | fix | ✅ |
| BL-029 | Security headers HTTP (X-Content-Type-Options, X-Frame-Options, CSP) | feat | ✅ |
| BL-030 | PIN — SHA-256 sans sel → scrypt (migration transparente) | fix | ✅ |
| BL-031 | `download_cookies_path` — valider et restreindre le chemin | fix | ✅ |
| BL-032 | `MEDIA_ROOT` global — thread-safety (`threading.Lock`) | fix | ✅ |
| BL-033 | `_jobs` — purge TTL des jobs terminés (fuite mémoire) | fix | ✅ |
| BL-034 | delete/move — DB-first pour l'atomicité (rollback si échec FS) | fix | ✅ |
| BL-035 | `init_db()` — index couvrant `idx_progress_active` | chore | ✅ |
| BL-036 | Logging — audit trail des opérations fichiers + IP cliente | feat | ✅ |
| BL-037 | Frontend — `apiFetch` timeout + feedback réseau (AbortController) | feat | ✅ |
| BL-038 | Gestes tactiles — overlay découverte au premier lancement | feat | ✅ |
| BL-039 | Accessibilité — aria-label, `:focus-visible`, contraste `--text-dim` | feat | ✅ |
| BL-064 | Fix — transcodage forcé malgré l'option désactivée | fix | ✅ |
| BL-065 | Fix — dialog d'aide clavier illisible (Firefox) | fix | ✅ |
