.PHONY: help install-backend install-frontend dev-backend dev-frontend test test-backend test-frontend lint format docker-up docker-down migrate seed-eval load-test

help:
	@echo "Targets: install-backend install-frontend dev-backend dev-frontend test lint format docker-up docker-down migrate seed-eval load-test"

install-backend:
	cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev -- --host 0.0.0.0

test: test-backend test-frontend

test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm test -- --run

lint:
	cd backend && ruff check app tests && mypy app
	cd frontend && npm run lint

format:
	cd backend && ruff format app tests && ruff check --fix app tests
	cd frontend && npm run format

docker-up:
	docker compose up --build

docker-down:
	docker compose down --remove-orphans

migrate:
	cd backend && alembic upgrade head

seed-eval:
	cd backend && python -m app.cli.seed_evaluation

load-test:
	locust -f load_tests/locustfile.py --host http://localhost:8000

