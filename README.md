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
- **Database**: Ready for Firestore, PostgreSQL, or your preferred database
- **Dev**: Docker Compose + pnpm workspaces + ESLint + Prettier

## Quick Start

1. **Set up Stytch authentication:**
   - Create a Stytch account at https://stytch.com
   - Create a new project in your Stytch dashboard
   - Copy your Project ID and Secret
   - Create a `.env` file in the `apps/api/` directory:
     ```bash
     # apps/api/.env
     STYTCH_PROJECT_ID=your_project_id_here
     STYTCH_SECRET=your_secret_here
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

### Project Structure

```
apps/
  web/          # React frontend
  api/          # FastAPI backend
packages/
  shared/       # Shared TypeScript types
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

Create environment files:

```bash
# apps/api/.env
STYTCH_PROJECT_ID=your_project_id_here
STYTCH_SECRET=your_secret_here
```

### 3. Start Development

```bash
# Option 1: Docker (recommended)
docker-compose up --build

# Option 2: Local development
pnpm dev:backend  # Terminal 1
pnpm dev:frontend # Terminal 2
```

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