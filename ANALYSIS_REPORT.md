# Repository Technical Due Diligence Analysis

This document contains the structural and architectural analysis of five repositories within the Enterprise AI Platform ecosystem. The analysis strictly documents the *actual* codebase state (files, folders, code logic) without inventing features or proposing redesigns.

---

## 1. IntentGraph (https://github.com/DARREN-2000/IntentGraph)

### 1. Executive Summary
IntentGraph is a Python library designed to build cross-file dependency graphs and code clusters from Python source code, providing machine-queryable context for AI agents. Note: There is a significant divergence between the README (which describes a Node.js/Next.js monorepo with Planners and Executors) and the actual repository contents, which are strictly a Python library.

### 2. Purpose
To parse Python codebases into a structured dependency graph of files, classes, functions, and imports using AST (Abstract Syntax Tree) parsing.

### 3. Current Features
- AST-based parsing of Python files.
- Cross-file dependency tracking (imports, function calls, class definitions).
- Directed graph construction using NetworkX.
- Exporting graph data to structured Pydantic models.
- Configurable directory traversal with exclusion rules.

### 4. Folder Structure
- `intentgraph/`: Core Python library source code (e.g., `graph.py`, `parser.py`, `orchestrator.py`).
- `tests/`: Pytest suite (`test_graph.py`, `test_parser.py`, etc.).
- `infra/`: Infrastructure as Code (Helm charts in `infra/helm/intentgraph`, Kubernetes manifests in `infra/k8s`, and Terraform modules in `infra/terraform`).
- `docs/`: Documentation, screenshots, and runbooks.

### 5. Architectural Pattern
Data Processing Pipeline / Library pattern. It operates as a batch analyzer: Ingest directory -> Parse AST -> Build NetworkX Graph -> Export to Pydantic.

### 6. Technologies
- **Language**: Python (>=3.12, <3.14)
- **Libraries**: NetworkX, Pydantic, Typer, AST (standard library)
- **Tooling**: Poetry, Pytest, Ruff, Mypy
- **Infrastructure**: Helm, Kubernetes (Kustomize), Terraform

### 7. Public APIs
The primary public Python API is the `Orchestrator` class (`intentgraph.orchestrator.Orchestrator.process_directory`). No network/HTTP APIs exist in the codebase.

### 8. Internal Components
- `CodeParser` (`intentgraph/parser.py`): Uses `ast.NodeVisitor` to extract symbols.
- `DependencyGraph` (`intentgraph/graph.py`): Wraps `nx.DiGraph` to build and store relationships.
- `Orchestrator` (`intentgraph/orchestrator.py`): Manages the directory traversal and coordinates parsing and graph building.

### 9. Domain Model
Defined in `intentgraph/models.py`:
- `Node`: Represents a code entity (file, class, function, import, module).
- `Edge`: Represents a relationship (`contains`, `calls`, `inherits`, `imports`).
- `GraphData`: Container for lists of Nodes and Edges.

### 10. Infrastructure
Located in `infra/`. Includes Terraform modules (`eks`, `rds`, `redis`, `s3`, `vpc`), Kubernetes base and overlays (`dev`, `staging`, `prod`), and a Helm chart.

### 11. Deployment
Intended for Kubernetes via the Helm chart (`infra/helm/intentgraph`), which specifies API and Worker deployments and an HPA.

### 12. CI/CD
Uses GitHub Actions (implied by `.github/workflows/` mentioned in README and standard practices).

### 13. Testing
Tested via Pytest. Test files exist in the `tests/` directory (e.g., `test_graph.py`). `pyproject.toml` configures `pytest` and `pytest-cov`.

### 14. Documentation Quality
Mixed. The repository contains extensive architecture docs (`docs/architecture/overview.md`), but the README describes a Node.js monorepo architecture that does not match the actual Python codebase. The Python code itself is clean but under-documented.

### 15. Current Strengths
Clean, robust AST parsing implementation. Good performance optimizations (avoiding Pydantic `model_dump()` overhead in loops as seen in `graph.py`). Strong IaC foundation in the `infra/` folder.

### 16. Current Weaknesses
Massive discrepancy between the README (claiming a Node.js web app, Temporal, CLI) and the actual codebase (a Python dependency graph library).

### 17. Technical Debt
The documentation is stale or describes a completely different system/iteration.

### 18. Missing Components
All frontend components (Next.js), Temporal workers, and Node.js backend services mentioned in the README are completely missing from the source code.

---

## 2. Inference Control Plane (https://github.com/DARREN-2000/Inference-Control-Plane)

### 1. Executive Summary
An asynchronous FastAPI-based AI gateway that provides routing, caching, rate limiting, and observability for LLM traffic.

### 2. Purpose
To act as a central proxy between client applications and external LLM providers, enforcing quotas, standardizing metrics, and reducing latency/costs via semantic caching.

### 3. Current Features
- Request proxying and model routing.
- User and API key-based rate limiting (Redis-backed).
- Semantic caching of LLM responses.
- OpenTelemetry (OTLP) and Prometheus metrics integration.
- Next.js frontend dashboard.

### 4. Folder Structure
- `src/inference_control_plane/`: FastAPI backend application.
- `frontend/`: Next.js web dashboard.
- `alembic/`: Database migration scripts.
- `deploy/kubernetes/`: Kubernetes deployment manifests.
- `tests/`: Pytest test suite.
- `docs/` and `website/`: Architecture documentation and Vite-based documentation site.

### 5. Architectural Pattern
API Gateway / Proxy with Middleware pattern. Requests flow through validation -> rate limiting -> cache lookup -> LLM routing -> logging.

### 6. Technologies
- **Backend**: Python 3.12, FastAPI, SQLAlchemy (asyncpg), Redis, Alembic, HTTPX.
- **Frontend**: Next.js, React, Tailwind CSS.
- **Observability**: OpenTelemetry, Prometheus.
- **Deployment**: Docker, Uvicorn.

### 7. Public APIs
Exposed via FastAPI (`src/inference_control_plane/api/`):
- `POST /api/v1/generate`: Main LLM inference endpoint.
- `GET /health/ready`, `GET /health/live`: Health checks.
- `GET /metrics`: Prometheus metrics.

### 8. Internal Components
- **API Router** (`api/`): Handles request parsing and dependency injection.
- **Services** (`services/`): `llm_client.py` for external API calls.
- **Data Access** (`db/`): Redis configuration and SQLAlchemy sessions.
- **Core** (`core/`): Exception handlers, configuration (`config.py`).
- **Observability** (`observability/`): Tracing and logging setup.

### 9. Domain Model
- Authentication: API Keys, Users.
- Operations: LLM Requests, Cache Entries, Rate Limit Counters.

### 10. Infrastructure
Provides a `Dockerfile` for containerization, a `docker-compose.yml` for local multi-service testing (Postgres, Redis), and Kustomize manifests in `deploy/kubernetes/`.

### 11. Deployment
Designed for stateless deployment (e.g., Render, Kubernetes) backed by managed PostgreSQL and Redis clusters.

### 12. CI/CD
GitHub Actions for testing, linting (`ruff`), type checking (`mypy`), and publishing Docker images to GHCR.

### 13. Testing
Comprehensive test suite in `tests/` utilizing `pytest` (e.g., `test_router.py`, `test_cache.py`, `test_settings.py`).

### 14. Documentation Quality
High. Clear `ARCHITECTURE.md` and `OPERATIONS.md`. Good inline documentation and clear setup instructions.

### 15. Current Strengths
Excellent observability integration (OTLP + Prometheus natively configured in `main.py`). Clean async Python architecture using modern tools (`uv` and `ruff`).

### 16. Current Weaknesses
Relies heavily on external Redis for caching and rate limiting; if Redis fails, gateway operations could be severely degraded.

### 17. Technical Debt
The worker process mentioned in the README currently uses the same image as the API, suggesting background task processing is not yet cleanly decoupled.

### 18. Missing Components
Advanced load balancing across multiple LLM provider credentials is not visibly complex.

---

## 3. GuardrailX (https://github.com/DARREN-2000/GuardrailX)

### 1. Executive Summary
A framework for building governance and security guardrails around LLM applications, featuring policy engines for content safety, PII redaction, and prompt injection.

### 2. Purpose
To intercept, evaluate, and potentially block or redact interactions with LLMs based on configurable compliance and security policies.

### 3. Current Features
- Policy evaluation (hallucination risk, jailbreak, PII redaction, content safety).
- Governance decision logging and auditing.
- Multi-tenant data model.
- FastAPI backend paired with a Vite/React frontend.

### 4. Folder Structure
- `backend/`: FastAPI application (`app/`), database migrations (`alembic/`).
- `frontend/`: Vite + React UI (`src/`).
- `policies/`: Individual policy evaluation logic (e.g., `content-safety/`, `pii-redaction/`).
- `infrastructure/`: Docker Compose, Kubernetes, Terraform, Grafana, Prometheus configs.
- `tests/`: End-to-end, integration, and unit tests.

### 5. Architectural Pattern
Interceptor / Policy Enforcement Point. It evaluates rules against payloads before passing them to/from the LLM.

### 6. Technologies
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Alembic, MLflow.
- **Frontend**: Node, Vite, React, Tailwind CSS.
- **Infrastructure**: Docker Compose, Terraform, Kubernetes.

### 7. Public APIs
- Health: `/api/v1/health/live`, `/api/v1/health/ready` (as seen in `backend/app/main.py`).
- Implied governance endpoints under `api_v1_prefix`.

### 8. Internal Components
Defined in `backend/app/models/__init__.py`:
- `Policy` and `PolicyVersion`
- `GovernanceDecision`
- `RiskAssessment`
- `AuditEvent`

### 9. Domain Model
Highly normalized relational model tracking `Tenant`s, `User`s, `Policy` definitions, and real-time `RiskAssessment`s and `GovernanceDecision`s.

### 10. Infrastructure
Extensive `infrastructure/` directory with templates for AWS/Terraform, Kubernetes manifests, and observability (Grafana/Prometheus).

### 11. Deployment
Can be run via `docker-compose` locally, or deployed to Kubernetes utilizing the provided manifests.

### 12. CI/CD
GitHub Actions (`ci.yml`, `deploy-pages.yml`).

### 13. Testing
Structured testing pyramid in `tests/` containing `e2e`, `fixtures`, `integration`, and `unit` folders. Run via `pytest`.

### 14. Documentation Quality
Very high. Includes `PRODUCT_DESIGN_DOCUMENT.md`, ADRs (`docs/adr/`), and distinct docs for architecture, compliance, and data models.

### 15. Current Strengths
Very strong domain modeling for compliance (separating Policy Versions from Decisions from Audit Events). Clear separation of concerns between backend, frontend, and policies.

### 16. Current Weaknesses
Heavy dependency on database availability; latency overhead of evaluating multiple ML-based policies per request.

### 17. Technical Debt
None immediately apparent from the structure.

### 18. Missing Components
While MLflow is integrated for tracking, specific model weights or external API dependencies for the ML policy evaluators (like PII detection) might require significant external configuration not bundled in the repo.

---

## 4. EnterpriseIQ (https://github.com/EnterpriseIQ/enterprise-knowledge-intelligence-platform)

### 1. Executive Summary
A secure Retrieval-Augmented Generation (RAG) platform emphasizing strict Role-Based Access Control (RBAC), hybrid retrieval, and grounded, hallucination-free generation.

### 2. Purpose
To allow enterprise users to query heterogeneous internal documents (PDFs, SQL, JSON) while mathematically guaranteeing they cannot access information above their clearance or outside their department.

### 3. Current Features
- Hybrid retrieval (ChromaDB dense vectors + BM25 sparse index).
- Multi-layer RBAC filtering (department, clearance, explicit ACL).
- Grounded extractive generation (defaults to zero-hallucination verbatim extraction).
- Confidence scoring and citation generation.
- Graceful degradation (fallback to hashing if ML embeddings fail).

### 4. Folder Structure
- `src/`: Core Python code (`api/`, `generation/`, `ingestion/`, `processing/`, `retrieval/`, `security/`, `vectorstore/`).
- `data/`: Synthetic data generation (`documents/`, `rbac/`).
- `tests/`: Comprehensive pytest suite.
- `website/`: Frontend documentation/dashboard (Vite).
- `docs/`, `diagrams/`: Architecture and runbooks.

### 5. Architectural Pattern
Data Pipeline (Ingestion -> Chunk -> Embed -> Store) and Query Pipeline (Route -> Retrieve -> RBAC -> Assemble -> Generate).

### 6. Technologies
- Python 3.10+, FastAPI, ChromaDB, SentenceTransformers, Rank-BM25.
- OpenTelemetry, Prometheus Client.
- Vite, React (frontend).

### 7. Public APIs
- `POST /query`: Main inference endpoint.
- `GET /roles`: List RBAC roles.
- `GET /health`: System health and active backends.
- `GET /audit`: Fetch recent audit trail.

### 8. Internal Components
- `RAGPipeline` (`src/pipeline.py`): Orchestrates the flow.
- `HybridRetriever`: Merges dense and sparse results.
- `RBAC` engine: Validates access per chunk.
- `AnswerGenerator`: Extractive text generator.

### 9. Domain Model
- `QueryRequest`, `QueryResponse`
- `RawDocument`, chunked text segments with inherited security metadata.

### 10. Infrastructure
Self-contained via `Dockerfile` and `docker-compose.yml`. Includes a `Makefile` for orchestration.

### 11. Deployment
Containerized. Runs entirely offline by default (using local ChromaDB and downloaded sentence-transformers).

### 12. CI/CD
GitHub Actions (`.github/workflows/ci.yml`) testing across Python 3.10-3.12.

### 13. Testing
Extensive test suite (`pytest -q`) covering RBAC leakage, performance, SQL injection prevention, and API contracts.

### 14. Documentation Quality
Excellent. Includes `architecture.md`, `security.md`, `evaluation.md`, and robust terminal-based demo transcripts (`sample_outputs.md`).

### 15. Current Strengths
Security-first architecture. The RBAC implementation is deeply integrated into the retrieval process. The offline capability and fallback mechanisms ensure high availability.

### 16. Current Weaknesses
Using local ChromaDB limits distributed, horizontal scaling out of the box.

### 17. Technical Debt
Audit trails and access policies rely heavily on local JSON/JSONL files (`data/rbac/access_policies.json`) rather than a managed database.

### 18. Missing Components
External Identity Provider (IdP) integration (SAML/OIDC). Distributed vector database support.

---

## 5. AI Hypervisor Platform (https://github.com/DARREN-2000/ai-hypervisor-platform)

### 1. Executive Summary
An opinionated virtualization control plane written in Go for managing and scheduling GPU-accelerated AI workloads across KVM/QEMU virtual machines.

### 2. Purpose
To provide a unified control plane for provisioning, orchestrating, and observing VMs tailored specifically for GPU workloads, including Multi-Instance GPU (MIG) partitioning.

### 3. Current Features
- API Server for VM and GPU management requests.
- Pluggable scheduler for VM placement (bin-packing, spread, NUMA-aware).
- Background task executor.
- OTLP and Prometheus metrics integration.

### 4. Folder Structure
- `cmd/`: Service entry points (`api-server`, `gpu-orchestrator`, `host-agent`, `resource-monitor`, `scheduler`, `task-executor`, `vm-manager`).
- `internal/`: Core logic (`api`, `gpu`, `libvirt`, `models`, `orchestrator`, `scheduler`, etc.).
- `pkg/`: Reusable libraries (`telemetry`, `errors`).
- `deploy/`: K8s manifests, Dockerfiles, Grafana dashboards.
- `docs/`: Architecture and API (OpenAPI spec).

### 5. Architectural Pattern
Event-Driven Microservices. Services coordinate via NATS messaging and use PostgreSQL as the authoritative state store, with Redis for caching/locking.

### 6. Technologies
- **Language**: Go 1.21.
- **Messaging**: NATS.
- **Datastore**: PostgreSQL, Redis.
- **Virtualization**: KVM/QEMU via Libvirt, NVML for GPUs.
- **Observability**: Prometheus, OpenTelemetry (OTLP).

### 7. Public APIs
REST API (`internal/api/` and `docs/api/openapi.yaml`):
- `/api/v1/vms` (CRUD actions for VMs, Start/Stop/Reboot)
- `/api/v1/gpus`
- `/api/v1/hosts`
- `/metrics`
- WebSockets for VM console and metric streams.

### 8. Internal Components
- **API Server**: Handles external ingress.
- **VM Manager**: Validates requests and writes desired state.
- **GPU Orchestrator**: Allocates GPU resources based on policies.
- **Host Agent**: DaemonSet interacting with local Libvirt/NVML.
- **Scheduler**: Determines host placement.

### 9. Domain Model
- `VirtualMachine`, `VMFlavor`, `VMImage`.
- `GPU`, `GPUAllocation`, `HostNode`, `Task` (defined in `openapi.yaml` and `internal/models`).

### 10. Infrastructure
Includes `deploy/kubernetes/` manifests, `deploy/docker/` configurations, and `deploy/grafana/` dashboard templates.

### 11. Deployment
Designed for Kubernetes. The control plane runs as standard Deployments, while the `host-agent` runs as a DaemonSet on GPU-enabled nodes.

### 12. CI/CD
GitHub Actions workflows (inferred from documentation) for publishing GHCR images.

### 13. Testing
`test/e2e/` folder exists for end-to-end testing, utilizing standard Go testing conventions.

### 14. Documentation Quality
Very high. Features a comprehensive `ARCHITECTURE.md`, `openapi.yaml`, and a GitHub Pages site (`docs/site/`) for animated visualization.

### 15. Current Strengths
Clear, modular Go architecture. Excellent domain separation into individual microservices (`cmd/`). Strong OpenAPI specification.

### 16. Current Weaknesses
Much of the codebase appears to be heavily scaffolded stubs. For example, `cmd/gpu-orchestrator/main.go` only parses config and sets up signals without starting a real service loop.

### 17. Technical Debt
Implementations for actual Libvirt commands and NVML bindings need to be fleshed out to move from scaffolding to a functional hypervisor.

### 18. Missing Components
Concrete implementations of the virtualization layers (Libvirt / KVM interaction logic) and real hardware metrics collectors are currently missing or mocked.
