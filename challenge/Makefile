# PYTHONPATH makes the sibling packages importable without installing them.
REPO_ROOT := $(shell cd .. && pwd)
PYTHONPATH := $(REPO_ROOT)/agentic-ai-toolkit/src:$(REPO_ROOT)/llm-eval-starter/src:$(CURDIR)/src
export PYTHONPATH

.PHONY: install demo test eval serve

install:
	pip install -e ../agentic-ai-toolkit -e ../llm-eval-starter -e .

demo:
	python examples/run_offline.py

test:
	python tests/test_smoke.py

eval:
	python -c "from challenge.evaluation import run_eval; s=run_eval('data/golden.jsonl'); print(s.stats.as_dict())"

serve:
	uvicorn challenge.app:app --reload
