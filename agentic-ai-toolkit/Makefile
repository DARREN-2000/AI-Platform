.PHONY: install test demo serve

install:
	pip install -e ".[dev]"

test:
	pytest -q

demo:
	python -m agentic_toolkit.cli agent "what is 21 * 2"
	python -m agentic_toolkit.cli rag "capital of France"

serve:
	pip install -e ".[serve]" && uvicorn serving.app:app --reload
