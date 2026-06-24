FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e ".[dev]"
ENTRYPOINT ["python", "-m", "agentic_toolkit.cli"]
CMD ["agent", "what is 21 * 2"]
