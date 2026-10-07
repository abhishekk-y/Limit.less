PYTHON ?= python

.PHONY: install dev-api dev-web migrate seed demo test lint typecheck build test-e2e
install:
	$(PYTHON) -m pip install -r apps/api/requirements-dev.txt
	npm --prefix apps/web ci

dev-api:
	$(PYTHON) -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000

dev-web:
	npm --prefix apps/web run dev

migrate:
	cd apps/api && $(PYTHON) -m alembic upgrade head

seed:
	$(PYTHON) scripts/seed_runtime.py

demo: seed

test:
	$(PYTHON) -m pytest tests -q

lint:
	$(PYTHON) -m ruff check apps/api/app/runtime packages/scoring/journey.py tests/api tests/scoring/test_journey.py
	npm --prefix apps/web run lint

typecheck:
	npm --prefix apps/web run type-check

build:
	npm --prefix apps/web run build

test-e2e:
	npm --prefix apps/web run test:e2e
