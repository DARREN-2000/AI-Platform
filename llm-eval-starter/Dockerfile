FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e ".[dev]"
ENTRYPOINT ["python", "-m", "llm_eval.cli"]
CMD ["--provider", "mock"]
