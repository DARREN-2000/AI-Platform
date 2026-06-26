# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder
ENV PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN pip install uv
COPY pyproject.toml ./
RUN uv pip install --system --requirement pyproject.toml || true
COPY . .

FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1
RUN useradd -m -u 10001 appuser
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/health').status==200 else sys.exit(1)" || exit 1
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
