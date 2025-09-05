# CyberCQBench Development Commands

.PHONY: help dev test lint build clean seed docker-build docker-up docker-down

help:
	@echo "CyberCQBench Development Commands"
	@echo "================================="
	@echo "dev              - Start full development environment (backend + frontend)"
	@echo "dev-stop         - Stop all development services"
	@echo "dev-logs         - View backend service logs"
	@echo "dev-status       - Check status of all services"
	@echo "dev-backend-only - Start only backend services (Docker)"
	@echo "dev-frontend     - Start only frontend development server"
	@echo "test             - Run backend tests"
	@echo "lint             - Run linting for all code"
	@echo "build            - Build production images"
	@echo "clean            - Clean up containers and volumes"
	@echo "seed             - Seed database with sample prompts"
	@echo "import-cysecbench - Import CySecBench dataset (50 prompts per category)"
	@echo "import-cysecbench-full - Import full CySecBench dataset (200 per category)"

# Development
dev:
	@echo "🚀 Starting CyberCQBench development environment..."
	@echo "📡 Starting backend services with Docker Compose..."
	@docker compose up -d --build
	@echo "⏳ Waiting for services to be ready..."
	@sleep 5
	@echo "✅ Backend services started!"
	@echo "🎨 Starting frontend development server..."
	@echo "📱 Frontend will be available at: http://localhost:3000"
	@echo "🔧 API will be available at: http://localhost:8000"
	@echo "📊 MongoDB Admin at: http://localhost:8081"
	@echo ""
	@echo "Press Ctrl+C to stop the frontend (backend will keep running)"
	@cd ui && npm install --silent && npm run dev

dev-stop:
	@echo "🛑 Stopping all development services..."
	@docker compose down
	@echo "✅ All services stopped!"

dev-logs:
	@docker compose logs -f

dev-status:
	@docker compose ps

dev-backend-only:
	docker compose up --build

dev-backend:
	cd app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	cd ui && npm install && npm run dev

# Testing
test:
	cd tests && python -m pytest -v --cov=../app

test-frontend:
	cd ui && npm test

# Linting and formatting
lint:
	cd app && ruff check . && black --check . && mypy .
	cd ui && npm run lint

format:
	cd app && ruff --fix . && black .
	cd ui && npm run lint --fix

# Building
build:
	docker-compose build

# Database operations
seed:
	python scripts/seed_data.py

import-cysecbench:
	@echo "📥 Importing CySecBench dataset (SOC/GRC/Incident Response scenarios)..."
	docker compose exec api python scripts/import_cysecbench.py 50
	@echo "✅ CySecBench dataset import complete!"

import-cysecbench-full:
	@echo "📥 Importing full CySecBench dataset (may take several minutes)..."
	docker compose exec api python scripts/import_cysecbench.py 200
	@echo "✅ Full CySecBench dataset import complete!"

# Document management
test-documents:
	@echo "🧪 Testing document upload and prompt generation..."
	@echo "Use the Documents page at http://localhost:3000/documents"

generate-prompts:
	@echo "🤖 Generate prompts from uploaded documents"
	@echo "Use the 'Generate Prompts' button on individual documents"

# Docker commands
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# Cleanup
clean:
	docker compose down -v
	docker system prune -f

# Production
prod:
	docker compose -f docker-compose.prod.yml up -d

# Install dependencies
install:
	pip install -r requirements.txt
	cd ui && npm install
