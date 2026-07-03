.PHONY: doctor dev up down api web worker test lint format clean zip

doctor:
	python -m hermes_agent.cli doctor

dev:
	docker compose up --build

up:
	docker compose up -d --build

down:
	docker compose down

api:
	PYTHONPATH=packages:. uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

worker:
	PYTHONPATH=packages:. python -m apps.worker.worker

web:
	cd apps/web && pnpm dev

test:
	PYTHONPATH=packages:. pytest -q

lint:
	ruff check .
	cd apps/web && pnpm lint

format:
	ruff format .

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache **/__pycache__ apps/web/.next apps/web/node_modules

zip:
	cd .. && zip -r hermes-agent-starter.zip hermes-agent-starter -x '*/node_modules/*' '*/.next/*' '*/.venv/*' '*/__pycache__/*'
