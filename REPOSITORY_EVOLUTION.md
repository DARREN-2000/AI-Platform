# Repository Evolution Plan

This document reviews the 5 core repositories of the Enterprise AI Platform individually. The goal is to evolve the existing architecture without redesigning from scratch, treating each repository as an independent bounded context with clear interfaces.

---

## 1. IntentGraph

*   **Current Architecture:** A Python library designed to parse Abstract Syntax Trees (AST) and build cross-file code dependency graphs. It orchestrates execution via an `Orchestrator` but is poorly documented, with a README that incorrectly describes a Node.js/Next.js application.
*   **Target Architecture:** A pure Python orchestration and dependency graph engine. It remains focused on building and executing DAGs, integrating with external platform tools via clean interfaces rather than trying to build monolithic web components.
*   **Required Refactoring:** Update the documentation to reflect reality. Refactor hardcoded dependencies to allow pluggable execution strategies.
    *   *Why:* Aligning documentation with the actual implementation is critical to avoid developer confusion. Decoupling dependencies allows the orchestrator to remain agnostic of external systems.
*   **New Modules:** `interfaces.py` to define strict contracts for external LLM calls or retrieval actions.
    *   *Why:* To ensure the DAG engine can interact with the rest of the Enterprise AI Platform without tight coupling.
*   **Files to Move:** Move any leftover or conceptual UI/Next.js files (if they exist) out of the repository.
    *   *Why:* Maintain single responsibility as a Python library.
*   **Files to Split:** Split `intentgraph/orchestrator.py` to separate graph parsing from graph execution logic.
    *   *Why:* Parsing an AST/graph and executing actions across it are distinct concerns (Single Responsibility Principle).
*   **Files to Merge:** Consolidate redundant graph modeling classes if present into a single `models.py`.
    *   *Why:* Centralizes data structures for ease of maintenance.
*   **Public Interfaces:** `Orchestrator.run(graph)`
*   **Internal Interfaces:** `GraphBuilder`, `ASTParser`.
*   **SDK Requirements:** Provide a lightweight, installable Python library (e.g., via Poetry) for other tools to invoke the parser.
*   **Testing Improvements:** Add integration tests that simulate graph execution without needing real source files.
    *   *Why:* Ensures the orchestrator can execute tasks deterministically.
*   **Documentation Improvements:** Rewrite `README.md` completely to remove Node.js/Next.js references.
    *   *Why:* To correctly document the Python API and library usage.
*   **Roadmap:**
    1. Fix documentation.
    2. Split parsing from execution logic.
    3. Implement pluggable interfaces for external platform actions.

---

## 2. Inference Control Plane

*   **Current Architecture:** FastAPI API Gateway acting as an LLM proxy. It relies heavily on Redis for rate limiting and caching. Background workers currently share the same API image and deployment context.
*   **Target Architecture:** High-performance, streaming-first LLM routing gateway. It handles connection management and failover, communicating with policies via high-speed gRPC and decoupling background tasks.
*   **Required Refactoring:** Extract background worker logic from the main API process/image.
    *   *Why:* Heavy background processing in the same image can cause latency spikes and resource starvation for the main latency-sensitive API proxy.
*   **New Modules:** `grpc_interceptor.py` for evaluating requests against GuardrailX.
    *   *Why:* HTTP REST interceptors add too much overhead. gRPC provides the low latency needed for a data-plane interceptor.
*   **Files to Move:** Move background worker code to a dedicated `worker/` directory.
    *   *Why:* Explicitly separates the deployment artifacts and concerns.
*   **Files to Split:** Split `src/inference_control_plane/api/main.py`. Separate route definitions from application initialization and middleware.
    *   *Why:* `main.py` tends to become a monolith; splitting it improves readability and testability.
*   **Files to Merge:** Merge duplicated or fragmented LLM client configurations into a unified `services/llm_client.py`.
    *   *Why:* Ensures consistent provider abstraction (e.g., timeouts, retries).
*   **Public Interfaces:** `POST /api/v1/generate`, `GET /metrics`.
*   **Internal Interfaces:** `LLMClient`, `CacheManager`, `RateLimiter`.
*   **SDK Requirements:** Expose a minimal HTTP client SDK for internal platform services to use this gateway seamlessly.
*   **Testing Improvements:** Introduce chaos testing for Redis failure scenarios.
    *   *Why:* Ensure the gateway fails open gracefully instead of collapsing when Redis is down.
*   **Documentation Improvements:** Document Redis dependency, caching strategies, and fallback behaviors.
    *   *Why:* Operators need to understand the failure domain of the gateway.
*   **Roadmap:**
    1. Decouple background workers.
    2. Implement gRPC interceptor client.
    3. Enhance failover strategies.

---

## 3. GuardrailX

*   **Current Architecture:** A multi-tenant policy enforcement point (FastAPI + Vite/React) that evaluates requests (hallucination, PII, etc.) and logs decisions to a relational database using MLflow.
*   **Target Architecture:** A stateless, high-speed evaluation engine queried synchronously via gRPC by the Inference Control Plane, with asynchronous database logging.
*   **Required Refactoring:** Move database interactions out of the critical synchronous evaluation path.
    *   *Why:* Database lookups and inserts add massive latency to every LLM request. Logging should be asynchronous.
*   **New Modules:** `eval_cache.py` (in-memory fast-path evaluation).
    *   *Why:* Caching recent or common risk assessments minimizes redundant ML model evaluations.
*   **Files to Move:** Move large ML model logic to a dedicated `models/` directory.
    *   *Why:* Cleanly separates heavy ML logic from the lightweight web backend logic.
*   **Files to Split:** Split `backend/app/main.py` into `api_routes.py` and `policy_engine.py`.
    *   *Why:* Separates HTTP concern from the core evaluation engine logic.
*   **Files to Merge:** Merge repetitive policy boilerplate into a base `PolicyEvaluator` class.
    *   *Why:* Reduces code duplication across different policy types (e.g., PII vs Content Safety).
*   **Public Interfaces:** `POST /api/v1/evaluate` (gRPC equivalent), `GET /api/v1/health/live`.
*   **Internal Interfaces:** `RiskEvaluator`, `DecisionLogger`.
*   **SDK Requirements:** Provide a shared protocol buffers (`.proto`) definition.
*   **Testing Improvements:** Implement strict mock testing for ML models.
    *   *Why:* Avoids downloading heavy model weights during CI/CD.
*   **Documentation Improvements:** Document external system dependencies required for specific ML policies (e.g., Presidio for PII).
    *   *Why:* Allows deployers to understand the infrastructure footprint.
*   **Roadmap:**
    1. Implement gRPC server.
    2. Decouple database logging to async workers.
    3. Add local caching.

---

## 4. EnterpriseIQ

*   **Current Architecture:** Python-based RAG pipeline using FastAPI and ChromaDB. It currently handles ingestion, chunking, strict RBAC, retrieval, *and* LLM-based generation.
*   **Target Architecture:** A pure enterprise knowledge retrieval engine with deeply embedded RBAC. It should only return relevant, permission-checked chunks, delegating text generation to the orchestrator/Inference Control Plane.
*   **Required Refactoring:** Strip out all LLM generation and "agentic" answering logic.
    *   *Why:* Prevents a split-brain architecture where multiple services are managing prompts and LLM context.
*   **New Modules:** `retrieval_api.py` serving a pure `POST /retrieve` endpoint returning raw chunks with citations.
    *   *Why:* Focuses the repository on its core competency: search and access control.
*   **Files to Move:** Move static RBAC files (`data/rbac/access_policies.json`) into a dedicated configuration structure or external database schema.
    *   *Why:* Hardcoded JSON files do not scale for dynamic enterprise identity management.
*   **Files to Split:** Split `src/pipeline.py` into `ingestion_pipeline.py` and `retrieval_pipeline.py`.
    *   *Why:* Ingestion is an asynchronous write-heavy task; retrieval is a synchronous read-heavy task. They should scale independently.
*   **Files to Merge:** Merge scattered text processing utilities into a unified `chunker.py`.
    *   *Why:* Centralizes the logic that dictates embedding quality.
*   **Public Interfaces:** `POST /retrieve`, `GET /roles`, `POST /ingest`.
*   **Internal Interfaces:** `RBACValidator`, `HybridSearcher`, `VectorStoreAdapter`.
*   **SDK Requirements:** Expose a lightweight Python SDK for IntentGraph to query context securely.
*   **Testing Improvements:** Expand the test suite specifically for RBAC boundary edge cases.
    *   *Why:* Ensuring zero data leakage is the primary value proposition of this service.
*   **Documentation Improvements:** Clarify that this is a retrieval-only service and document the expected JWT/token passing format for RBAC.
    *   *Why:* Integrators need to know how to pass identity context.
*   **Roadmap:**
    1. Remove text generation logic.
    2. Split ingestion from retrieval.
    3. Migrate RBAC from static JSON to a robust data store.

---

## 5. AI Hypervisor Platform

*   **Current Architecture:** Go-based event-driven microservices architecture managing VM/GPU virtualization via NATS and Postgres. Heavily scaffolded with many mocked functionalities.
*   **Target Architecture:** Concrete virtualization control plane that dynamically provisions GPU resources based on asynchronous capacity requests from the Inference Control Plane.
*   **Required Refactoring:** Replace scaffolding and mocked endpoints with real concrete implementations.
    *   *Why:* The hypervisor cannot orchestrate real workloads until the stubs are replaced with actual driver calls.
*   **New Modules:** `capacity_listener.go` listening to NATS for `model.capacity.requested` events.
    *   *Why:* Enables dynamic, asynchronous scaling of infrastructure based on data-plane traffic depth without synchronous coupling.
*   **Files to Move:** Move unimplemented commands out of `cmd/` into an `experiments/` or `draft/` folder.
    *   *Why:* Avoids confusion over what is currently production-ready.
*   **Files to Split:** Split `internal/orchestrator/` into `gpu_allocator.go` and `vm_scheduler.go`.
    *   *Why:* Scheduling VMs and partitioning GPUs (e.g., MIG) are distinct resource management problems.
*   **Files to Merge:** Consolidate NATS connection and listener boilerplate into a shared `pkg/messaging` library.
    *   *Why:* Reduces repeated code across the various microservices.
*   **Public Interfaces:** `GET /api/v1/vms`, `POST /api/v1/gpus`.
*   **Internal Interfaces:** `LibvirtDriver`, `NVMLClient`, `Scheduler`.
*   **SDK Requirements:** Automatically generate a Go/Python client SDK directly from `docs/api/openapi.yaml`.
*   **Testing Improvements:** Add hardware-in-the-loop tests for actual Libvirt and NVML interactions.
    *   *Why:* Standard unit tests cannot catch real-world driver or hypervisor failures.
*   **Documentation Improvements:** Update documentation to explicitly outline which features are mocked vs. fully implemented.
    *   *Why:* Sets accurate expectations for users trying to deploy the platform.
*   **Roadmap:**
    1. Implement concrete Libvirt/NVML bindings.
    2. Add capacity NATS listener.
    3. Finalize the VM scheduler.
