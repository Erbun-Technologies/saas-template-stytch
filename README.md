# SaaS Template

A production-ready SaaS application template with modern authentication, user management, and a full-stack TypeScript setup. Perfect for quickly bootstrapping your next SaaS project.

## ✨ Features

- 🔐 **Authentication**: Stytch integration with secure session management
- 👤 **User Management**: Complete user registration, login, and profile management
- 🎨 **Modern UI**: React 18 + Tailwind CSS + shadcn/ui components
- 🚀 **Full-Stack TypeScript**: Shared types between frontend and backend
- 📱 **Responsive Design**: Mobile-first approach with modern UX patterns
- 🔄 **Real-time Ready**: WebSocket support for real-time features
- 🐳 **Docker Support**: Containerized development and deployment
- 📦 **Monorepo**: pnpm workspaces for efficient dependency management

## 🛠 Tech Stack

- **Frontend**: Vite + React 18 + TypeScript + TanStack Router + TanStack Query + Zustand
- **Backend**: FastAPI + Python 3.12 + Pydantic v2
- **UI**: Tailwind CSS + shadcn/ui + Lucide React icons
- **Auth**: Stytch (with HTTP-only cookies and bearer tokens)
- **Database**: PostgreSQL in Docker (tables auto-created)
- **Dev**: Docker Compose + pnpm workspaces + ESLint + Prettier

## Quick Start

1. **Set up Stytch authentication:**
   - Create a Stytch account at https://stytch.com
   - Create a new project in your Stytch dashboard
   - Copy your Project ID and Secret
   - Create a `.env` file in the `apps/api/` directory (or copy from example):
     ```bash
     # apps/api/.env
     STYTCH_PROJECT_ID=your_project_id_here
     STYTCH_SECRET=your_secret_here
     DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/saas
     ```
   - Also create a web env file (or copy from example) and set your Stytch public token:
     ```bash
     # apps/web/.env
     VITE_STYTCH_PUBLIC_TOKEN=your_stytch_public_token
     VITE_API_URL=http://localhost:8000
     VITE_APP_NAME=SaaS Template
     ```

2. **Start the development environment:**
   ```bash
   docker-compose up --build
   ```

3. **Access the applications:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Test authentication:**
   - Go to http://localhost:5173
   - Sign up or log in
   - Check the dashboard to see both frontend and backend authentication status

## Development

### Local Development (without Docker)

1. **Install dependencies:**
   ```bash
   pnpm install
   ```

2. **Start backend:**
   ```bash
   pnpm --filter api dev
   ```

3. **Start frontend:**
   ```bash
   pnpm --filter web dev
   ```

### Make Targets

- `make dev`: Start full stack with Docker Compose.
- `make dev-frontend`: Run frontend locally via Vite.
- `make dev-backend`: Run backend locally with Uvicorn.
- `make db-up`: Start only the Postgres service.
- `make db-shell`: Open a `psql` shell to the `saas` database.

### AI Assistance (Cursor)

- This repo includes Cursor rules in `.cursor/rules/` to guide AI agents:
  - `project-agent.mdc` and `project-inline.mdc`: global conventions and guardrails.
  - `frontend-agent.mdc` / `frontend-inline.mdc`: Vite/React + TanStack patterns; do not edit `routeTree.gen.ts` (run `pnpm --filter web run generate:routes`).
  - `backend-agent.mdc`: FastAPI + async SQLAlchemy usage; prefer `apps/api/db/crud.py` for DB access.

### Project Structure

```
apps/
  web/          # React frontend
  api/          # FastAPI backend
packages/
  shared/       # Shared TypeScript types

.env examples
  apps/api/.env.example  # API secrets and DATABASE_URL
  apps/web/.env.example  # VITE_API_URL and Stytch public token

db (runtime)
  PostgreSQL runs via docker-compose service `db`
```

## 🚀 Getting Started

### Prerequisites

- Node.js 20+ 
- Python 3.12+
- pnpm
- Docker (optional, for containerized development)

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd saas-template-stytch
pnpm install
```

### 2. Environment Setup

Create environment files (or copy examples):

```bash
# API
cp apps/api/.env.example apps/api/.env

# Web
cp apps/web/.env.example apps/web/.env
# Optional override (defaults to Postgres service in Compose)
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/saas
```

### 3. Start Development

```bash
# Option 1: Docker (recommended)
docker-compose up --build

# Option 2: Local development
pnpm dev:backend  # Terminal 1
pnpm dev:frontend # Terminal 2
```

### Database

- Compose starts a Postgres `db` service with defaults:
  - `POSTGRES_DB=saas`, `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgres`
  - Connection: `postgresql+asyncpg://postgres:postgres@db:5432/saas`
- The API creates the `users` table on startup (template-only). Use `make db-shell` to open `psql`.

### Endpoints

- `GET /health` – liveness check.
- `GET /health/db` – database connectivity and user count.
- `GET /auth/me` – authenticated session status via Stytch.
- `GET /users/me` – current user profile from the template DB.

### DBeaver (local)

- Host: `localhost`, Port: `5432`, DB: `saas`, User: `postgres`, Password: `postgres`
- URL: `postgresql://postgres:postgres@localhost:5432/saas`

### CI

GitHub Actions workflow runs type checks and a basic API import check on pushes and PRs.

### Branding

- Frontend app name: set `VITE_APP_NAME` in `apps/web/.env` to change the navbar title.
- Backend title/description: set `APP_NAME` in `apps/api/.env` to change the FastAPI docs title.

## 📁 Project Structure

```
├── apps/
│   ├── web/          # React frontend (Vite + TypeScript)
│   └── api/          # FastAPI backend (Python)
├── packages/
│   └── shared/       # Shared TypeScript types
└── .cursor/          # Cursor IDE rules and conventions
```

## 🎯 What's Included

- ✅ **Authentication Flow**: Complete signup/login with Stytch
- ✅ **Protected Routes**: Route guards and authentication middleware
- ✅ **User Dashboard**: Example dashboard with auth status
- ✅ **API Integration**: Frontend-backend communication patterns
- ✅ **Type Safety**: Shared TypeScript types across the stack
- ✅ **Modern UI**: Responsive design with Tailwind CSS
- ✅ **Development Tools**: Hot reload, linting, type checking

## 🔧 Customization

This template is designed to be easily customizable:

1. **Branding**: Update the app name, colors, and logos
2. **Features**: Add your specific business logic and features
3. **Database**: Connect your preferred database (Firestore, PostgreSQL, etc.)
4. **Styling**: Customize the Tailwind theme and components
5. **Authentication**: Extend or replace Stytch with your preferred auth provider

## 📚 Learn More

- [TanStack Router](https://tanstack.com/router) - File-based routing
- [TanStack Query](https://tanstack.com/query) - Data fetching and caching
- [Stytch](https://stytch.com) - Authentication platform
- [FastAPI](https://fastapi.tiangolo.com) - Python web framework
- [shadcn/ui](https://ui.shadcn.com) - UI component library

## 🤝 Contributing

This is a template repository. Feel free to fork and customize for your needs!

## 📄 License

MIT License - feel free to use this template for your projects.
