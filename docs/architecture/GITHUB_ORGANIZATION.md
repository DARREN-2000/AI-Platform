# Enterprise AI Platform GitHub Organization

This document defines the GitHub Organization design for the Enterprise AI Platform. It provides a blueprint for structuring repositories, shared libraries, CI/CD pipelines, and standards across the ecosystem to ensure independent releases and loose coupling.

## Organization Structure

The GitHub Organization (`@enterprise-ai-platform`) is structured as a collection of independent repositories representing bounded contexts. This architecture avoids a monolithic structure, optimizing for modularity, independent scalability, and distinct release cycles.

### Repository Structure

**Core Platform Services (Independent Repositories):**

*   `intentgraph`: The top-level agentic orchestrator. Handles natural language parsing, DAG planning, and user intent execution.
*   `enterpriseiq`: The Enterprise Retrieval Engine (RAG). Handles document ingestion, vectorization, RBAC filtering, and context retrieval.
*   `inference-control-plane`: The primary LLM Gateway. Handles routing, rate limiting, connection management, caching, and model offloading.
*   `guardrailx`: The stateless Security and Governance evaluation engine. Enforces policies like PII redaction and jailbreak prevention.
*   `ai-hypervisor-platform`: The asynchronous infrastructure control plane. Provisions and orchestrates GPU workloads and local models.

**Shared Resource Repositories:**

*   `platform-docs`: Centralized documentation, architecture decision records (ADRs), and unified OpenAPI catalogs.
*   `platform-sdk`: The core shared SDK containing libraries for telemetry, authentication, configuration, and internal clients.
*   `infrastructure-as-code`: Terraform modules and shared Kubernetes helm charts for platform deployment.
*   `github-actions-templates`: Shared reusable GitHub Actions workflows for consistent CI/CD across all services.

---

## Shared Strategies & Components

### The "Why" of Centralized Sharing

All shared components are extracted into distinct repositories (`platform-sdk`, `infrastructure-as-code`, `github-actions-templates`) rather than duplicated across individual services.

**Why centralize?**
1.  **Consistency:** Security protocols, telemetry schemas, and CI pipelines must be uniform to guarantee platform-wide compliance and observability.
2.  **Maintainability:** Updating a core dependency (e.g., patching an OpenTelemetry vulnerability) happens in one SDK repository, seamlessly cascading to services via package bumps, avoiding cross-repo sync nightmares.
3.  **Loose Coupling:** Individual microservices consume shared resources as versioned artifacts. They remain unaware of each other's internals.
4.  **Independent Releases:** A change in the shared SDK produces a new semantic version. Repositories update at their own pace, preventing lock-step deployment bottlenecks associated with monorepos.

### Shared SDK

Housed in `platform-sdk`, this multi-language repository provides foundational libraries.

*   **Design:** Published as versioned packages (`pip install enterprise-ai-sdk`, `go get github.com/enterprise-ai-platform/sdk`).
*   **Contents:** Standardized database connection pools, error handling schemas, HTTP client wrappers (with built-in circuit breakers and retries), and gRPC proto definitions.
*   **Why Shared:** Ensures all platform microservices handle networking, retries, and errors identically without duplicating complex resilience logic.

### Shared Documentation

Housed in `platform-docs`.

*   **Design:** A central Backstage or MkDocs repository.
*   **Contents:** Architecture map, API catalogs (auto-generated from OpenAPI specs), runbooks, and developer onboarding.
*   **Why Shared:** Provides a single pane of glass for the entire distributed system. Developers don't need to hunt through 5 separate repos to understand the holistic request flow.

### Shared Authentication

Part of `platform-sdk` (`sdk/auth`).

*   **Design:** A standardized JWT validation library connecting to a central OIDC provider (e.g., Keycloak).
*   **Contents:** Middleware for extracting tokens, validating signatures, and parsing tenant claims.
*   **Why Shared:** Authentication is a critical security boundary. Implementing token validation manually in every repo risks a single vulnerable implementation compromising the whole platform.

### Shared Logging

Part of `platform-sdk` (`sdk/logging`).

*   **Design:** Standardized structured JSON logger (e.g., `structlog` for Python, `zap` for Go).
*   **Contents:** Automatic injection of `x-request-id`, tenant ID, and timestamp into every log line.
*   **Why Shared:** Required for centralized log aggregation (ELK/Splunk) to parse logs uniformly across all services for cross-repo debugging.

### Shared Configuration

Part of `platform-sdk` (`sdk/config`).

*   **Design:** Centralized environment variable parsing standard.
*   **Contents:** Shared Pydantic models (Python) or Viper setups (Go) for handling core configs like database URIs, log levels, and vault integration.
*   **Why Shared:** Prevents subtle bugs caused by inconsistent configuration parsing across different services.

### Shared Telemetry

Part of `platform-sdk` (`sdk/telemetry`).

*   **Design:** OpenTelemetry (OTLP) instrumentation.
*   **Contents:** Automatic distributed tracing, context propagation middleware, and standard Prometheus metric endpoints (`/metrics`).
*   **Why Shared:** Distributed tracing only works if every service in the chain correctly propagates the `traceparent` header. A shared library guarantees this context is never dropped.

### Shared RBAC

Part of `platform-sdk` (`sdk/rbac`) and central IAM.

*   **Design:** Standardized Zero-Trust schema.
*   **Contents:** Schema definitions for user roles, department clearance, and evaluation logic.
*   **Why Shared:** Authorization rules must mean the same thing in `IntentGraph` as they do in `EnterpriseIQ`. A shared library ensures consistent policy interpretation.

### Shared Release Process

Defined in `github-actions-templates`.

*   **Design:** Standardized Semantic Versioning (SemVer).
*   **Contents:** Automated generation of changelogs, GitHub releases, and Docker image tags based on Conventional Commits.
*   **Why Shared:** Ensures that checking out `v1.2.3` of `guardrailx` means the same level of stability and release process rigor as `v1.2.3` of `enterpriseiq`.

### Shared Versioning

Defined in `github-actions-templates`.

*   **Design:** Strict Semantic Versioning triggered by commit prefixes (`feat:`, `fix:`, `BREAKING CHANGE:`).
*   **Contents:** Git tags map 1:1 with container image tags published to GHCR.
*   **Why Shared:** Predictable dependency management. Services rely on API contracts, and SemVer provides strict guarantees about contract stability.

### Shared CI/CD & GitHub Actions

Housed in `github-actions-templates`.

*   **Design:** Centralized `.github/workflows` utilizing reusable workflows (`workflow_call`).
*   **Contents:** Standardized pipelines for linting, testing, security scanning (Trivy/SonarQube), and building multi-arch Docker images.
*   **Why Shared:** Enforces uniform quality gates. A vulnerability scan update made in the central template instantly applies to all 5 microservices on their next PR.

### Shared Coding Standards

Housed in `.github` (org-wide repository) and `.ai/` standards.

*   **Design:** Unified linting configurations (`.eslintrc`, `ruff.toml`, `golangci-lint.yaml`).
*   **Contents:** Pre-commit hooks and style guides.
*   **Why Shared:** Reduces cognitive load for developers moving between bounded contexts. A Python file in `IntentGraph` should read similarly to a Python file in `Inference Control Plane`.

### Shared OpenAPI Strategy

Housed in `platform-docs` and `platform-sdk`.

*   **Design:** API First approach.
*   **Contents:** Every repo must define its REST interfaces via OpenAPI 3.0 specs. These are aggregated centrally.
*   **Why Shared:** Enables automated client generation, contract testing between loosely coupled services, and centralized API documentation.

### Shared Package Strategy

*   **Design:** Private package registries (GitHub Packages for npm/PyPI/Docker).
*   **Contents:** Publishing `platform-sdk` modules.
*   **Why Shared:** Protects proprietary code while mimicking standard open-source package consumption for developers.

### Shared Docker Strategy

Defined in `github-actions-templates`.

*   **Design:** Distroless or Alpine base images.
*   **Contents:** Standardized multi-stage builds ensuring minimal attack surface, non-root execution, and consistent labeling.
*   **Why Shared:** Simplifies vulnerability management and ensures operational consistency in Kubernetes.

### Shared Kubernetes Strategy

Housed in `infrastructure-as-code`.

*   **Design:** Standardized deployment patterns.
*   **Contents:** Kustomize bases or core Helm templates defining standard resource requests/limits, liveness/readiness probes, and PodDisruptionBudgets.
*   **Why Shared:** Prevents "snowflake" deployments. Operations teams can manage all services uniformly.

### Shared Helm Strategy

Housed in `infrastructure-as-code`.

*   **Design:** A shared `enterprise-service-chart`.
*   **Contents:** A generic Helm chart that individual repos configure via `values.yaml` (e.g., injecting specific image tags and env vars).
*   **Why Shared:** Drastically reduces boilerplate. Developers only define what makes their service unique, inheriting platform best practices automatically.

### Shared Terraform Strategy

Housed in `infrastructure-as-code`.

*   **Design:** Modular Terraform architecture.
*   **Contents:** Modules for provisioning underlying cloud resources (VPCs, EKS clusters, Managed Redis, NATS, PostgreSQL).
*   **Why Shared:** Infrastructure spans multiple services. A single Terraform state manages the foundational layer that the loosely coupled microservices run on top of.

### Shared Observability & Monitoring

Defined via `platform-sdk` (instrumentation) and `infrastructure-as-code` (infrastructure).

*   **Design:** Centralized Prometheus, Grafana, and Jaeger/Tempo stack.
*   **Contents:** Standardized dashboards tracking RED metrics (Rate, Errors, Duration) for every service automatically.
*   **Why Shared:** Allows tracking a request across the entire platform. When a user intent fails, tracing shows exactly whether it died in `IntentGraph`, `GuardrailX`, or the `LLM`.

### Shared Security

Governed by `GuardrailX`, `platform-auth`, and `github-actions-templates`.

*   **Design:** Defense in depth.
*   **Contents:** Dependency scanning in CI, container scanning in the registry, mTLS service mesh in Kubernetes, and centralized LLM governance via `GuardrailX`.
*   **Why Shared:** Security cannot be an afterthought in individual repos. Centralized enforcement ensures compliance standards (SOC2, HIPAA) are met universally across the architecture.
