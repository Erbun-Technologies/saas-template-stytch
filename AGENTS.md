# Repository Guidelines

## Project Structure & Module Organization
- `apps/web`: React + Vite frontend (TypeScript, Tailwind, TanStack Router/Query).
- `apps/api`: FastAPI backend (Python 3.12, Pydantic, Stytch).
- `packages/shared`: Shared TypeScript types/utilities.
- Root tooling: `docker-compose.yml`, `Makefile`, `pnpm-workspace.yaml`.

## Build, Test, and Development Commands
- `make dev`: Start full stack via Docker Compose (frontend + backend).
- `make dev-frontend`: Run Vite dev server locally (`http://localhost:5173`).
- `make dev-backend`: Run FastAPI locally with auto-reload on port `8000`.
- `pnpm dev`: Same as `docker-compose up --build` (monorepo script).
- `pnpm dev:frontend` / `pnpm dev:backend`: Filtered local dev for each app.
- `pnpm build`: Recursive build for all workspaces.
- `pnpm type-check`: Type-check all TypeScript packages.

Examples
- Frontend only: `pnpm --filter web dev`
- Build frontend: `pnpm --filter web build` then `pnpm --filter web preview`

## Coding Style & Naming Conventions
- TypeScript: 2-space indent; camelCase for vars, PascalCase for components; colocate UI in `apps/web/src/components`.
- Routes: TanStack file-based routes in `apps/web/src/routes` (e.g., `login.tsx`, `dashboard.tsx`). Route tree is generated via `pnpm --filter web run generate:routes` and outputs `routeTree.gen.ts` (do not edit).
- Python: 4-space indent; snake_case for modules/functions; keep FastAPI routers in modular packages (e.g., `apps/api/auth`).

## Testing Guidelines
- No test suite is bundled yet. For contributions:
  - Frontend: prefer Vitest; name files `*.test.tsx` alongside source.
  - Backend: prefer pytest; name files `test_*.py` under `apps/api/`.
  - Keep unit tests fast; add minimal integration tests for auth flows.

## Commit & Pull Request Guidelines
- Commits: Imperative, concise subject (≤72 chars). Example: `api: add CSRF token endpoint` or `web: fix dashboard auth state`.
- PRs: Clear description, scope (web/api/shared), steps to test, screenshots for UI, and linked issues. Ensure `pnpm type-check` and local run pass.

## Security & Configuration Tips
- Secrets: Put Stytch creds in `apps/api/.env` (`STYTCH_PROJECT_ID`, `STYTCH_SECRET`). Do not commit `.env`.
- Frontend API base: `VITE_API_URL` (set in Compose) should point to the API (default `http://localhost:8000`).
- Cookies/CSRF: API sets CSRF cookie and supports double-submit; avoid logging tokens or secrets.

