# Hoard — Copilot Instructions

## Project Overview

**Hoard** 🐦 is a self-hosted media browser and video player for a Synology NAS.
Core features: filesystem browser (raw, no metadata library), watch progress tracking (seen / in progress / unseen), integrated HTML5 player with touch gestures, file management (move, delete), configurable settings with optional PIN lock.

## Tech Stack

| Layer        | Technology                                              |
|-------------|----------------------------------------------------------|
| Backend     | Python 3.12+, FastAPI, uvicorn                           |
| Database    | SQLite (via native `sqlite3` — no ORM)                   |
| Frontend    | Vanilla HTML/CSS/JS — single file `frontend/index.html`  |
| Deployment  | Docker Compose (Synology NAS target)                     |
| Testing     | pytest + httpx                                           |
| Linting     | ruff (lint + format)                                     |

## Development Principles

### Code Quality

- **Code language**: All code (variables, functions, comments, commit messages) MUST be in **English**.
- **Linting**: `ruff` is the single tool for linting AND formatting Python code. Zero warnings policy.
- **No mypy** — the project is untyped by design (simplicity first).
- **No build step** — the frontend is a single `index.html` file; no bundler, no framework.
- **VS Code integration**: ruff and Pylance report errors directly in VS Code. Fix all reported issues before considering code complete.

### Documentation

- **Documentation MUST be kept up to date** with every code change.
- **Bilingual**: All documentation files must be written in **both English and French**, as separate files under `docs/` (e.g. `user-guide.en.md` / `user-guide.fr.md`).
- Code-level comments are in **English only**.
- Update relevant docs in the SAME commit as the code change.

### Architecture Rules

- **Backend** (`backend/main.py`):
  - Everything lives in a single file — keep it that way unless complexity forces a split.
  - Routes are thin; helper functions handle logic.
  - All DB access goes through the `get_db()` context manager (returns a `sqlite3.Connection`).
  - Use Pydantic models for ALL POST request bodies.
  - `safe_path()` MUST be called on every user-supplied path to prevent path traversal.
  - Configuration via environment variables (`MEDIA_ROOT`, `DB_PATH`, `PREDEFINED_FOLDERS`).

- **Frontend** (`frontend/index.html`):
  - Single file — inline CSS and JS. No external dependencies beyond what the browser provides natively.
  - Global `cfg` object holds all settings loaded from `/api/settings` at startup.
  - Touch gesture constants come from `cfg`, never hardcoded.
  - `localStorage` is only used for `volume` (device-local). Everything else is in the backend DB.

- **Database** (SQLite, native `sqlite3`):
  - Schema is created on startup via `init_db()` — no migration tool.
  - Tables: `progress` (watch state), `settings` (key/value), `quick_folders`.
  - Never use raw string concatenation for SQL — always use parameterised queries.

### Project Structure

```
hoard/
├── .github/
│   ├── copilot-instructions.md    # This file
│   └── workflows/
│       ├── ci.yml                 # Lint + tests on every push/PR
│       └── docker-build.yml       # Build Docker image on main / tags
├── pyproject.toml                 # pytest + ruff config
├── requirements-dev.txt           # Dev dependencies (fastapi, uvicorn, pytest, httpx, ruff)
├── Dockerfile
├── docker-compose.yml             # Production (Synology)
├── docker-compose.dev.yml         # Dev override (hot-reload + local volume)
├── backend/
│   ├── main.py                    # All backend logic (FastAPI)
│   └── requirements.txt
├── frontend/
│   └── index.html                 # Entire UI (inline CSS + JS)
├── tests/
│   ├── conftest.py                # pytest fixtures + env isolation
│   └── test_api.py                # API tests via httpx.AsyncClient
├── docs/                          # Documentation (EN + FR paired files)
│   ├── user-guide.en.md / user-guide.fr.md
│   ├── installation.en.md / installation.fr.md
│   ├── developer.en.md / developer.fr.md
│   └── getting-started.en.md / getting-started.fr.md
├── dev-media/                     # Local test media (gitignored)
├── CLAUDE.md                      # Project context (French)
├── ROADMAP.md
└── README.md
```

### Git safety rules

- **Never switch branches** (`git checkout`, `git switch`) without asking the user first.
- **Never push** to any remote without explicit user confirmation.
- **Never force-push**, reset hard, or delete branches without explicit user confirmation.
- Always confirm the current branch with `git branch` before committing if there is any doubt.

### Commit workflow

When the user asks to commit, follow these steps **in order** before creating the commit:

1. **Tests** — verify existing tests still pass; add or update tests for all new/changed backend behavior.
2. **Quality checks** — run all checks and fix all issues before proceeding:
   - `ruff check .`
   - `ruff format --check .`
   - `python -m pytest tests/`
3. **Documentation** — update relevant `docs/*.en.md` and `docs/*.fr.md` files if the change affects user-facing behavior or architecture.
4. **CHANGELOG** — add an entry under `## [Unreleased]` in `CHANGELOG.md` describing the change.
5. **Commit** — stage all modified files (code + tests + docs + CHANGELOG) and commit in one clean commit with a descriptive Conventional Commits message.

### PR preparation workflow

When the user asks to prepare a PR, follow these steps in order:

1. **Tests** — verify existing tests still pass; add or complete tests for all new/changed behavior.
2. **Documentation** — verify and update all relevant docs (EN + FR).
3. **Quality checks** — run ruff check, ruff format --check, pytest; fix all issues.
4. **Temporary PR description** — create a temporary markdown file (`.github/pull_request_description.md`) to help the user fill in the PR on GitHub. This file must **not** be committed.
   - The PR description **must be written in English**.
   - Keep it **concise**: one short summary paragraph + a bullet list of key changes.
5. **Commit** — one clean commit. Do **not** commit the PR description file.

### Release workflow

When the user asks to do a release, follow these steps in order:

1. **Propose a version number** — suggest a semver version based on the changes since the last release, and ask the user to confirm before proceeding.
2. **Write release notes** — draft concise, user-focused release notes **in both English and French**.
   - Structure: short intro sentence + bullet list of notable changes. No technical jargon.
   - Present them to the user for confirmation before continuing.
3. **Bump version** — update `version` in `pyproject.toml`.
4. **CHANGELOG** — move all entries from `## [Unreleased]` to a new `## [vX.Y.Z] - YYYY-MM-DD` section.
5. **Quality checks** — run ruff + pytest; fix all issues before proceeding.
6. **Commit** — one clean commit: `release: vX.Y.Z`.
7. **Tag** — create an annotated git tag `vX.Y.Z`.
8. **Push** — ask the user before pushing the commit and tag to GitHub.

### Commands

> **Version policy**: Never change the version number in `pyproject.toml` unless the user has confirmed it.

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/ -v
python -m pytest tests/ --cov=backend    # with coverage

# Lint + format
ruff check .
ruff format .
ruff format --check .                    # CI check (no writes)

# Dev server (activate venv first)
$env:MEDIA_ROOT = "d:\path\to\videos"
$env:DB_PATH    = "$env:TEMP\hoard_dev.db"
uvicorn backend.main:app --reload --port 8000
# → http://localhost:8000

# Docker
docker compose up --build               # Build & run
docker compose up -d                    # Run detached
docker compose -f docker-compose.dev.yml up  # Dev with hot-reload
```

### Naming Conventions

| Element            | Convention        | Example                   |
|-------------------|-------------------|---------------------------|
| Python files      | snake_case        | `main.py`                 |
| Python functions  | snake_case        | `safe_path()`             |
| Python constants  | UPPER_SNAKE_CASE  | `MEDIA_ROOT`              |
| Private helpers   | `_` prefix        | `_read_all_settings()`    |
| JS functions      | camelCase         | `toggleVideoFit()`        |
| JS globals        | camelCase         | `cfg`, `currentFile`      |
| CSS ids/classes   | kebab-case        | `#pin-screen`, `.ctrl-btn`|
| API endpoints     | kebab-case        | `/api/quick-folders`      |
| DB tables         | snake_case        | `quick_folders`           |
| DB columns        | snake_case        | `updated_at`              |
| Test files        | `test_` prefix    | `test_api.py`             |


## Development Principles

### TDD — Test-Driven Development

- **Always write tests BEFORE implementation code.**
- Workflow: Red → Green → Refactor.
  1. Write a failing test that defines the expected behavior.
  2. Write the minimum code to make the test pass.
  3. Refactor while keeping tests green.
- Every new feature, bugfix, or behavior change MUST start with a test.
- Test files mirror source structure: `budgie/services/budget_engine.py` → `tests/test_services/test_budget_engine.py`.
- Use fixtures and factories for test data (see `tests/conftest.py`) — avoid hardcoding.
- Aim for high coverage on business logic (services, importers, categorization). API routes tested via `httpx.AsyncClient`.

### Code Quality

- **Code language**: All code (variables, functions, classes, comments, docstrings, commit messages) MUST be in **English**.
- **Type hints**: All Python functions must have complete type annotations. `mypy` must pass with zero errors.
- **Linting**: `ruff` is the single tool for linting AND formatting Python code. Zero warnings policy.
- **VS Code integration**: The project is configured so that ruff, mypy, Pylance, ESLint and Vue language tools report errors/warnings directly in VS Code. Fix all reported issues before considering code complete.
- **Docstrings**: Use Google-style docstrings for all public functions, classes, and modules.
- **No magic numbers**: Use constants or enums. Monetary amounts are always in **integer centimes** (e.g., `1050` = 10.50€).

### Documentation

- **Documentation MUST be kept up to date** with every code change.
- **Bilingual**: All documentation files must be written in **both English and French**, in separate files under `docs/en/` and `docs/fr/`.
- Code-level documentation (docstrings, inline comments) is in **English only**.
- Update relevant docs in the SAME commit/PR as the code change.

### Architecture Rules

- **Backend**:
  - Layered architecture: `api/` (routes) → `services/` (business logic) → `models/` (ORM) / `schemas/` (Pydantic).
  - Routes must be thin — delegate logic to services.
  - All database operations go through SQLAlchemy async sessions.
  - Use Pydantic schemas for ALL request/response validation.
  - Configuration via `pydantic-settings` loading from `.env`.

- **Frontend**:
  - Use Vue 3 Composition API with `<script setup lang="ts">` syntax.
  - State management via Pinia stores.
  - API calls centralized in `src/api/` module using axios.
  - Components should be small, single-responsibility.
  - Use DaisyUI component classes — avoid custom CSS when a DaisyUI component exists.
  - **After every change to a `.vue` file, run `npx vue-tsc --noEmit -p tsconfig.app.json` (frontend equivalent of `mypy`) before considering the task done.** This catches template errors, broken bindings, and type mismatches that Vite only reports at runtime. Always use `-p tsconfig.app.json` to ensure all strict options (e.g. `noUncheckedIndexedAccess`) are applied — matching exactly what the CI runs.

- **Database**:
  - Monetary values are **integer centimes** (never floats).
  - Use Alembic for ALL schema changes — never modify the DB manually.
  - Unique constraints for deduplication (e.g., `import_hash` on transactions).

### Project Structure

```
budgie/
├── .github/
│   └── copilot-instructions.md   # This file
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── alembic.ini
├── alembic/
│   └── versions/
├── budgie/                        # Backend Python package
│   ├── __init__.py
│   ├── config.py                  # Pydantic Settings
│   ├── database.py                # SQLAlchemy engine & session
│   ├── main.py                    # FastAPI app
│   ├── models/                    # SQLAlchemy ORM models
│   ├── schemas/                   # Pydantic request/response schemas
│   ├── api/                       # FastAPI routers
│   ├── services/                  # Business logic
│   └── importers/                 # Bank file parsers
├── frontend/                      # Vue.js 3 SPA
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── api/                   # HTTP client
│       ├── components/            # Reusable Vue components
│       ├── views/                 # Page-level components
│       ├── stores/                # Pinia stores
│       └── router/                # Vue Router
├── tests/                         # Backend tests
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_importers/
├── docs/                          # Documentation (EN + FR)
│   ├── en/
│   │   ├── user-guide.md
│   │   └── developer-guide.md
│   └── fr/
│       ├── user-guide.md
│       └── developer-guide.md
└── data/                          # Runtime data (gitignored)
```

### Commit workflow

When the user asks to commit, follow these steps **in order** before creating the commit:

1. **Tests** — verify existing tests still pass; add or update tests for all new/changed behavior.
2. **Quality checks** — run all checks and fix all issues before proceeding:
   - Backend: `poetry run ruff check .`, `poetry run ruff format --check .`, `poetry run mypy budgie/`, `poetry run pytest`
   - Frontend: `cd frontend && npx vue-tsc --noEmit -p tsconfig.app.json`, `cd frontend && npx vue-tsc --noEmit` (CI-exact, no `-p`), `npx eslint src/`, `npx vitest run`
3. **Documentation** — verify and update all relevant docs:
   - `docs/en/` and `docs/fr/` user/developer guides — update if the change affects user-facing behavior or architecture.
   - Docstrings — update if public API signatures or behavior changed.
4. **Commit** — stage all modified files (code + tests + docs) and commit in one clean commit with a descriptive message.

### PR preparation workflow

When the user asks to prepare a PR, follow these steps in order:

1. **Tests** — verify existing tests still pass; add or complete tests for all new/changed behavior.
2. **Documentation** — verify and update all relevant docs (user guides EN + FR, README, docstrings).
3. **Quality checks** — run all backend and frontend checks; fix all issues before proceeding.
4. **Temporary PR description** — create a temporary markdown file (e.g. `.github/pull_request_description.md`) to help the user fill in the PR on GitHub. This file must **not** be committed.
   - The PR description **must be written in English**.
   - Keep it **concise**: one short summary paragraph + a bullet list of key changes. No lengthy prose.
5. **Commit** — commit all the above changes (tests, docs) in one clean commit. Do **not** commit the PR description file.

### Release workflow

When the user asks to do a release, follow these steps in order:

1. **Propose a version number** — suggest a semver version based on the changes since the last release (patch / minor / major), and ask the user to confirm before proceeding.
2. **Write release notes** — draft concise, user-focused release notes **in both English and French**.
   - Structure: short intro sentence + bullet list of notable changes. No technical jargon.
   - Present them to the user for confirmation before continuing.
3. **Bump version** — update `version` in `pyproject.toml` to the confirmed value.
4. **Update README** — update any version-specific info if needed.
5. **Quality checks** — run all backend and frontend checks; fix all issues before proceeding.
6. **Commit** — one clean commit: `release: vX.Y.Z`.
7. **Tag** — create an annotated git tag `vX.Y.Z`.
8. **Push** — ask the user before pushing the commit and tag to GitHub.

### Commands

> **Version policy**: Never change the version number in `pyproject.toml` or anywhere else unless the user has confirmed it.

```bash
# Backend
poetry install                          # Install dependencies
poetry run pytest                       # Run tests
poetry run pytest --cov=budgie          # Run tests with coverage
poetry run ruff check .                 # Lint
poetry run ruff format .                # Format
poetry run mypy budgie/                 # Type checking
poetry run uvicorn budgie.main:app --reload  # Dev server

# Frontend
cd frontend
npm install                             # Install dependencies
npm run dev                             # Vite dev server
npm run build                           # Production build
npx vitest run                          # Tests
npx eslint src/                         # ESLint
npx vue-tsc --noEmit -p tsconfig.app.json  # TypeScript check (matches CI exactly)

# Docker
docker compose up --build               # Build & run
docker compose up -d                    # Run detached
```

### Naming Conventions

| Element            | Convention        | Example                          |
|-------------------|-------------------|----------------------------------|
| Python files      | snake_case        | `budget_engine.py`               |
| Python classes    | PascalCase        | `BudgetAllocation`               |
| Python functions  | snake_case        | `get_month_budget()`             |
| Python constants  | UPPER_SNAKE_CASE  | `MAX_IMPORT_SIZE`                |
| Private helpers   | `_` prefix        | `_parse_amount()`               |
| Vue components    | PascalCase        | `EnvelopeCard.vue`               |
| Vue composables   | camelCase, `use`  | `useBudget.ts`                   |
| TypeScript files  | camelCase         | `apiClient.ts`                   |
| API endpoints     | kebab-case        | `/api/category-groups`           |
| DB tables         | snake_case plural | `budget_allocations`             |
| DB columns        | snake_case        | `auto_category_id`               |
| Test files        | `test_` prefix    | `test_budget_engine.py`          |
