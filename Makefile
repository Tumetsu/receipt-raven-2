.PHONY: help install dev-app dev-frontend db-up db-down migrate migrate-new api-client \
	test test-backend test-frontend lint lint-fix format lint-frontend deps-check deps-graph \
	duplication-check check docker-build docker-up template-update

# Compose v2 as a Docker CLI plugin (`docker compose`), or the standalone
# binary (`docker-compose`) that Homebrew and some Linux packages install.
COMPOSE ?= $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo docker-compose)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install backend and frontend dependencies
	cd backend && uv sync
	npm install

# Development

db-up: ## Start the development Postgres in Docker
	$(COMPOSE) -f docker-compose.dev.yml up -d --wait

db-down: ## Stop the development Postgres
	$(COMPOSE) -f docker-compose.dev.yml down

dev-app: ## Run the backend dev server on :8000
	cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run the Vite dev server on :5173 (proxies /api to :8000)
	npm run dev --workspace=frontend

migrate: ## Apply database migrations (alembic upgrade head)
	cd backend && uv run alembic upgrade head

migrate-new: ## Create a migration from model changes (usage: make migrate-new msg="add tags")
	cd backend && uv run alembic revision --autogenerate -m "$(msg)"

api-client: ## Export the OpenAPI schema and regenerate the frontend API client (no running backend needed)
	cd backend && uv run python scripts/export_openapi.py
	cd frontend && npm run api:generate

# Quality

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && uv run pytest

test-frontend: ## Run frontend tests (Vitest, browser mode)
	cd frontend && npm run test

lint: ## Backend: ruff, pyright and the import-linter architecture contracts
	cd backend && uv run ruff check .
	cd backend && uv run pyright
	cd backend && uv run lint-imports

lint-fix: ## Backend: fix what ruff can, then format
	cd backend && uv run ruff check --fix .
	cd backend && uv run ruff format .

format: ## Format backend (ruff) and frontend (prettier)
	cd backend && uv run ruff format .
	cd frontend && npm run format

lint-frontend: ## Frontend: prettier, oxlint, tsc, knip and dependency-cruiser
	cd frontend && npm run format:check
	cd frontend && npm run lint
	cd frontend && npm run type-check
	cd frontend && npm run knip
	cd frontend && npm run deps:check

deps-check: ## Check frontend module boundaries (dependency-cruiser)
	cd frontend && npm run deps:check

deps-graph: ## Print the frontend dependency graph as Mermaid
	@cd frontend && npm run --silent deps:graph

# Copy/paste detector (jscpd). Each stack's .jscpd.json holds a threshold that
# is a ratchet: lower it as duplication drops, never raise it.
duplication-check: ## Report copy-paste duplication in both stacks (jscpd)
	cd backend && npx jscpd --no-tips
	cd frontend && npm run duplication-check

check: lint lint-frontend duplication-check test ## Everything CI runs
	cd backend && uv run ruff format --check .

# Docker

docker-build: ## Build the production image
	docker build -t $(notdir $(CURDIR)):latest .

docker-up: ## Run the app and Postgres with docker compose (http://localhost:8000)
	$(COMPOSE) up --build

# Template

template-update: ## Pull the latest version of the project template (copier update)
	uvx copier update --trust --conflict rej
