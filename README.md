# Enterprise AI Platform Architecture

This document synthesizes an architectural transformation plan for unifying the five core repositories into one cohesive open-source Enterprise AI Platform.

## Phase 1: Repository Review

*   **IntentGraph**
    *   **Purpose:** Agent orchestration, planning, workflow execution, memory, DAG execution.
    *   **Current State:** Primarily Python backend for dependency graph parsing/orchestration, with some Next.js web components mentioned in README. Needs better separation of core logic from web UI.
    *   **Missing:** Standardized integration with a centralized LLM gateway (currently likely using direct API calls) and a unified policy engine.
*   **Inference Control Plane**
    *   **Purpose:** LLM routing, provider abstraction, caching, rate limiting, failover, traffic management.
    *   **Current State:** FastAPI application providing an OpenAI-compatible API interface. Built for scale with Redis/PostgreSQL.
    *   **Missing:** Deeper integration with GuardrailX to ensure all outgoing traffic is governed.
*   **GuardrailX**
    *   **Purpose:** Enterprise AI governance, prompt injection detection, jailbreak prevention, PII protection, policy enforcement.
    *   **Current State:** FastAPI backend with policy engine capabilities.
    *   **Missing:** A low-latency interceptor/proxy mode to sit seamlessly in front of the Inference Control Plane.
*   **EnterpriseIQ (enterprise-knowledge-intelligence-platform)**
    *   **Purpose:** Enterprise Agentic RAG platform with hybrid retrieval and enterprise knowledge management.
    *   **Current State:** Python-based retrieval pipeline with strict RBAC and citing capabilities.
    *   **Missing:** Decoupling from its own internal LLM generation logic to rely on the Inference Control Plane for generation.
*   **AI Hypervisor Platform**
    *   **Purpose:** GPU-aware virtualization, compute isolation, workload placement, AI infrastructure layer.
    *   **Current State:** Go-based control plane for KVM/QEMU, orchestrating GPUs.
    *   **Missing:** High-level dynamic provisioning hooks for Inference Control Plane to spin up/down models based on traffic.

## Phase 2: Architectural Map

The platform consists of five interconnected layers:

1.  **Layer 1: Infrastructure & Compute (AI Hypervisor Platform)** - Bottom layer, providing physical/virtual GPU resources.
2.  **Layer 2: Data & Knowledge (EnterpriseIQ)** - Data ingestion, vectorization, RBAC-filtered retrieval.
3.  **Layer 3: Security & Governance (GuardrailX)** - Sits as a policy enforcement point.
4.  **Layer 4: Core Inference (Inference Control Plane)** - LLM gateway.
5.  **Layer 5: Orchestration (IntentGraph)** - Top layer executing user intents using tools and lower layers.

## Phase 3: Dependency Graph

*   `IntentGraph` depends on `GuardrailX` (for prompt/action validation) and `EnterpriseIQ` (for RAG).
*   `EnterpriseIQ` depends on `GuardrailX` (for query/response validation).
*   `GuardrailX` acts as a middleware, forwarding requests to `Inference Control Plane`.
*   `Inference Control Plane` depends on `AI Hypervisor Platform` (to schedule local models on GPUs) and External LLMs.

## Phase 4: Interfaces

*   **REST API (OpenAI Compatible):** `GuardrailX` exposes an OpenAI-compatible API to `IntentGraph` and `EnterpriseIQ`, filtering traffic, then forwarding to `Inference Control Plane` via the same standard interface.
*   **gRPC/NATS:** `Inference Control Plane` to `AI Hypervisor Platform` for high-performance telemetry and dynamic scaling of GPU resources.
*   **REST API:** `IntentGraph` to `EnterpriseIQ` for `/query` retrieval.
*   **Shared SDK:** A unified Python SDK (`platform-sdk`) for all inter-service communication to handle retries, tracing, and auth.

## Phase 5: Shared Libraries

1.  `platform-telemetry`: OpenTelemetry setup for tracing (OTLP) and unified logging across Python and Go.
2.  `platform-auth`: JWT validation, OIDC integration, and standard RBAC schemas.
3.  `platform-client`: Standardized async HTTP/gRPC clients for internal service-to-service communication.
4.  `platform-models`: Shared Pydantic/Go models for common data structures (e.g., User, Tenant, Request Context).

## Phase 6: GitHub Organization Structure

```
ai-platform/
├── intentgraph               # Core agent orchestration
├── inference-control-plane   # LLM routing gateway
├── guardrailx                # Policy & governance
├── enterpriseiq              # Knowledge & RAG engine
├── ai-hypervisor-platform    # Compute infrastructure
├── docs                      # Platform-wide documentation & architecture
├── sdk                       # Shared libraries (telemetry, auth, clients)
├── deployments               # GitOps, Kubernetes manifests, Helm charts
└── examples                  # E2E sample apps
```

## Phase 7: Shared Concerns

*   **Authentication & RBAC:** Central OIDC provider (Keycloak/Auth0). All services validate JWTs using the shared `platform-auth` library.
*   **Logging & Telemetry:** All services use `platform-telemetry` to push OpenTelemetry traces and structured JSON logs with correlation IDs (`x-request-id`) to a central collector.
*   **Configuration:** Standardized `.env` parsing across Python (Pydantic Settings) and Go (Viper). Secrets managed via external store (Vault/K8s Secrets).
*   **Versioning & Releases:** Semantic versioning with automated GitHub Actions pushing to GHCR (`ghcr.io/ai-platform/*`).
*   **Documentation:** Centralized Backstage or MkDocs repository (`docs/`) pulling OpenAPI specs from all services.
