.PHONY: install test lint fmt demo serve docker-build docker-run compose-up compose-down k8s-deploy k8s-delete

install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check . && black --check .

fmt:
	ruff check --fix . && black .

demo:
	python -m agentic_toolkit.cli agent "what is 21 * 2"
	python -m agentic_toolkit.cli rag "capital of France"

serve:
	pip install -e ".[serve]" && uvicorn serving.app:app --reload

docker-build:
	docker build -t agentic-ai-toolkit:latest .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env agentic-ai-toolkit:latest

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down

k8s-deploy:
	kubectl apply -k deploy/k8s

k8s-delete:
	kubectl delete -k deploy/k8s
