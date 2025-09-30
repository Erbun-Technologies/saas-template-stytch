.PHONY: dev build clean install

# Default target
dev:
	@echo "🚀 Starting SaaS Template development environment..."
	docker-compose up --build

# Build all services
build:
	@echo "🔨 Building all services..."
	docker-compose build

# Clean up containers and images
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down --volumes --remove-orphans
	docker system prune -f

# Install dependencies locally (for development without Docker)
install:
	@echo "📦 Installing dependencies..."
	pnpm install

# Run frontend locally
dev-frontend:
	@echo "🌐 Starting frontend development server..."
	pnpm --filter web dev

# Run backend locally (requires Python environment)
dev-backend:
	@echo "⚡ Starting backend development server..."
	@echo "⚠️  Note: This requires Python 3.12+ and virtual environment"
	cd apps/api && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Show help
help:
	@echo "Available commands:"
	@echo "  make dev          - Start development environment with Docker Compose"
	@echo "  make build        - Build all Docker services"
	@echo "  make clean        - Clean up Docker resources"
	@echo "  make install      - Install dependencies locally"
	@echo "  make dev-frontend - Run frontend locally (requires pnpm)"
	@echo "  make dev-backend  - Run backend locally (requires Python 3.12+)"
	@echo "  make help         - Show this help message"

# Database helpers
.PHONY: db-up db-shell
db-up:
	@echo "🗄️  Starting Postgres (detached) ..."
	docker-compose up -d db

db-shell:
	@echo "🐘 Opening psql shell ..."
	docker-compose exec db psql -U postgres -d saas
