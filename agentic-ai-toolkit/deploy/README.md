# Deploying the Agentic Toolkit

The service is configured entirely through environment variables, so adapting it
to a challenge is usually just editing `.env` (Docker) or the ConfigMap (k8s) -
not the code.

| Variable | Default | Purpose |
|---|---|---|
| `AGENTIC_PROVIDER` | `rules` | `rules` (offline, no keys), `openai`, or `anthropic` |
| `AGENTIC_MODEL` | provider default | model name override |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | - | only for real providers |
| `AGENTIC_DOCS_PATH` | built-in demo docs | newline-delimited docs file for RAG |
| `PORT` | `8000` | HTTP port |

Endpoints: `GET /health`, `POST /chat {"question": "...", "k": 3}`.

## Docker

```bash
docker build -t agentic-ai-toolkit:latest .
cp .env.example .env          # edit only if using a real provider
docker run --rm -p 8000:8000 --env-file .env agentic-ai-toolkit:latest
curl localhost:8000/health
```

## docker compose

```bash
docker compose up --build -d
curl localhost:8000/health
docker compose down
```

## Kubernetes (kustomize)

```bash
docker build -t agentic-ai-toolkit:latest .   # make the image pullable by your cluster
# (kind: `kind load docker-image agentic-ai-toolkit:latest`; minikube: `minikube image load ...`)
kubectl apply -k deploy/k8s
kubectl -n agentic-toolkit get pods
kubectl -n agentic-toolkit port-forward svc/agentic-toolkit 8000:80
curl localhost:8000/health
```

The bundle installs: Namespace, ConfigMap, Deployment (2 replicas, liveness +
readiness probes on `/health`, CPU/memory requests & limits), Service
(ClusterIP), Ingress, and a HorizontalPodAutoscaler (2-6 replicas at 70% CPU).

### Using a real provider

1. `cp deploy/k8s/secret.example.yaml deploy/k8s/secret.yaml` and fill in keys.
2. Add `- secret.yaml` to `resources:` in `deploy/k8s/kustomization.yaml`.
3. Set `AGENTIC_PROVIDER: "openai"` (or `anthropic`) in `configmap.yaml`.
4. `kubectl apply -k deploy/k8s`.

The Deployment references the Secret with `optional: true`, so the default
offline `rules` provider runs without any Secret present.
