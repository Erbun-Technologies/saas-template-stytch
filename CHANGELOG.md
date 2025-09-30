# Changelog

## 0.1.0 - 2025-09-30

- Add PostgreSQL service via Docker Compose with healthcheck and persistent volume.
- Implement async SQLAlchemy DB layer (engine/session/models) and auto table creation on startup.
- Add `users` table with fields: `id`, `stytch_user_id`, `email`, `name`, `created_at`, `last_login`.
- Persist user on first authenticated backend call; update `last_login` on each auth.
- API endpoints: `GET /auth/me`, `GET /users/me`, `GET /health`, `GET /health/db`.
- Frontend dashboard: cards for Backend Authentication, Database Health, and Profile (DB).
- Env templates: `apps/api/.env.example`, `apps/web/.env.example`.
- Branding: `APP_NAME` (API) and `VITE_APP_NAME` (web) support.
- Align frontend API URL env to `VITE_API_URL` (fallback to `VITE_API_BASE_URL`).
- CI: Type-check monorepo, build web, basic API import check.
- CORS: include `http://web:5173` for Docker dev service.

