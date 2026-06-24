.PHONY: install test eval baseline

install:
	pip install -e ".[dev]"

test:
	pytest -q

eval:
	python -m llm_eval.cli --provider mock

baseline:
	python -m llm_eval.cli --provider mock --update-baseline
