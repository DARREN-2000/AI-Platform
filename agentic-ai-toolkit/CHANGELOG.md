# Changelog

## 0.1.0

- Initial release.
- Core (stdlib-only, offline): LangGraph-style agent `Graph` + ReAct loop, tool
  registry with a safe calculator, TF-IDF / hashing RAG, span tracer,
  reliability primitives (idempotency, token bucket, HMAC, retries), and a
  composable `ChatService`.
- Env-driven FastAPI serving layer (`serving/app.py`, `create_app()`).
- Deployment: production `Dockerfile`, `docker-compose.yml`, and a Kubernetes +
  kustomize bundle (namespace, configmap, optional secret, deployment with
  probes, service, ingress, HPA).
- Tooling/CI: unit tests + offline demos, Docker build & container smoke test,
  ruff/black/mypy config, pre-commit hooks, devcontainer, and a runnable
  `examples/quickstart.py`.
