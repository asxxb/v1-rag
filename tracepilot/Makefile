.PHONY: install up down logs test seed ingest eval

PYTHON = python
PIP = pip

install:
	$(PIP) install -r requirements.txt

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f

test:
	$(PYTHON) -m pytest tests/

seed:
	$(PYTHON) -m scripts.seed_database

ingest:
	$(PYTHON) -m scripts.ingest_documents

eval:
	$(PYTHON) -m evals.evaluator
