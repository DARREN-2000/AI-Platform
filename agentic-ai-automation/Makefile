.PHONY: install dev test lint format run docker clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check .
	mypy .

format:
	ruff format .
	ruff check --fix .

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

docker:
	docker compose up --build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache *.egg-info build dist
