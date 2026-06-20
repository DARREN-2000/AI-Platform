# Inference Control Plane - V2 Architecture Design

The Inference Control Plane serves as the single LLM gateway and data plane for the Enterprise AI Platform. It handles routing, connection management, streaming, rate limiting, caching, and failover for all LLM inference requests. It is the only component that communicates directly with external LLM providers and local hosted models.

## 1. Folder Structure

```text
inference-control-plane/
├── app/
│   ├── api/
│   │   ├── dependencies/
│   │   ├── routes/
│   │   │   ├── v1/
│   │   │   └── health.py
│   │   └── server.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   ├── db/
│   │   ├── migrations/
│   │   ├── models/
│   │   └── session.py
│   ├── events/
│   │   ├── publisher.py
│   │   └── nats_client.py
│   ├── gateway/
│   │   ├── router.py
│   │   ├── providers/
│   │   ├── load_balancer.py
│   │   └── rate_limiter.py
│   ├── interceptors/
│   │   └── guardrailx_grpc.py
│   ├── schemas/
│   │   ├── request.py
│   │   └── response.py
│   └── services/
│       ├── inference.py
│       └── metrics.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── deploy/
│   ├── Dockerfile
│   └── helm/
├── pyproject.toml
├── alembic.ini
└── README.md
```

## 2. Package Structure

- **`app.api`**: FastAPI application setup, middleware, and HTTP route definitions.
- **`app.core`**: Cross-cutting concerns like configuration, logging, and custom exception handling.
- **`app.db`**: SQLAlchemy models, database session management, and Alembic migrations.
- **`app.events`**: NATS publisher logic for asynchronous communication with AI Hypervisor Platform.
- **`app.gateway`**: The core routing engine. Handles provider abstractions, load balancing, fallback logic, and rate limiting (via Redis).
- **`app.interceptors`**: High-speed gRPC clients to interact with GuardrailX for policy evaluation.
- **`app.schemas`**: Pydantic models for API requests, responses, and internal data validation.
- **`app.services`**: Business logic coordinating the gateway, interceptors, and database.

## 3. Interfaces

- **External API (HTTP/REST)**: Exposes an OpenAI-compatible API for IntentGraph and other internal services.
- **GuardrailX (gRPC)**: Synchronous, low-latency gRPC calls to the GuardrailX sidecar for prompt/response evaluation.
- **AI Hypervisor Platform (NATS)**: Asynchronous event publishing for capacity requests and endpoint registration listening.
- **LLM Providers (HTTP/REST)**: Standard async HTTP calls to OpenAI, Anthropic, or local VLLM endpoints.

## 4. Domain Model

- **Tenant**: Represents an organizational unit with specific rate limits, quotas, and allowed providers.
- **APIKey**: Authentication tokens for tenants.
- **Route / Endpoint**: A destination LLM model (e.g., `gpt-4`, `llama-3-8b-local`).
- **InferenceRequest**: A logged request representing an attempt to generate text.
- **ProviderCache**: A representation of cached responses to avoid redundant LLM calls.

## 5. API Specification

**Base URL**: `/v1`

- `POST /v1/chat/completions`: OpenAI-compatible endpoint for chat generation. Supports streaming via SSE.
- `POST /v1/embeddings`: OpenAI-compatible endpoint for text embeddings.
- `GET /v1/models`: Returns a list of available models (dynamic based on AI Hypervisor registrations).
- `POST /v1/internal/endpoints`: (Internal) Webhook or API for AI Hypervisor Platform to register newly provisioned model endpoints.

## 6. Database Schema (PostgreSQL)

- **`tenants`**: `id`, `name`, `tier`, `created_at`, `updated_at`
- **`api_keys`**: `id`, `tenant_id`, `hashed_key`, `created_at`, `expires_at`, `is_active`
- **`rate_limits`**: `id`, `tenant_id`, `tokens_per_minute`, `requests_per_minute`
- **`request_logs`**: `id`, `tenant_id`, `model`, `prompt_tokens`, `completion_tokens`, `latency_ms`, `status_code`, `timestamp`
- **`registered_endpoints`**: `id`, `model_name`, `provider`, `url`, `status`, `last_health_check`

*(Note: High-throughput caching and real-time rate limiting will use Redis)*

## 7. Event Model (NATS)

**Published Events**:
- `model.capacity.requested`: Emitted when queue depth for a specific model exceeds a threshold.
  - Payload: `{ "model_name": "llama-3-8b", "current_queue_depth": 150, "target_latency_ms": 500 }`

**Subscribed Events**:
- `model.endpoint.ready`: Emitted by AI Hypervisor when a new model instance is ready to receive traffic.
  - Payload: `{ "model_name": "llama-3-8b", "endpoint_url": "http://node-5:8000/v1" }`
- `model.endpoint.offline`: Emitted by AI Hypervisor when a node is taken down.

## 8. Deployment Model

- **Compute**: Deployed as a stateless, horizontally scalable Kubernetes Deployment.
- **Sidecar**: GuardrailX is deployed as a DaemonSet or sidecar container in the same pod to ensure near-zero latency for gRPC policy checks.
- **Ingress**: Sits behind an NGINX or Envoy ingress controller to handle TLS termination.
- **Datastores**: Connects to a highly available Redis cluster and a PostgreSQL database.

## 9. Testing Strategy

- **Unit Tests**: `pytest` for testing gateway routing logic, rate limiting algorithms, and Pydantic validation. Mock external HTTP calls.
- **Integration Tests**: `pytest-asyncio` and `testcontainers` (Redis, PostgreSQL) to test DB sessions, rate limiting persistence, and gRPC interactions with a mock GuardrailX.
- **E2E Tests**: Load testing with `locust` or `k6` to verify streaming performance and ensure the NATS capacity events trigger correctly under load.

## 10. Roadmap

1.  **Phase 1**: Implement core OpenAI-compatible API, basic provider routing, and Redis rate limiting.
2.  **Phase 2**: Integrate high-speed gRPC interceptor for GuardrailX policy checks.
3.  **Phase 3**: Implement streaming support (Server-Sent Events) and semantic caching.
4.  **Phase 4**: Add NATS integration for async capacity management with the AI Hypervisor Platform.
5.  **Phase 5**: Advanced load balancing algorithms (least outstanding requests) across multiple local endpoints.
