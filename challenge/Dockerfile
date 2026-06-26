# Minimal container for the challenge service. Builds on the sibling packages.
FROM python:3.11-slim

WORKDIR /app

# Copy the whole monorepo context (build from repo root: docker build -f challenge/Dockerfile .)
COPY agentic-ai-toolkit /app/agentic-ai-toolkit
COPY llm-eval-starter /app/llm-eval-starter
COPY challenge /app/challenge

RUN pip install --no-cache-dir -e /app/agentic-ai-toolkit -e /app/llm-eval-starter \
    && pip install --no-cache-dir -e "/app/challenge[serve]"

ENV CHALLENGE_PROVIDER=rules \
    PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE 8000
CMD ["uvicorn", "challenge.app:app", "--host", "0.0.0.0", "--port", "8000"]
