# GuardrailX - V2 Architecture Design

GuardrailX is the high-speed, stateless enterprise AI governance engine. In the V2 architecture, it has been stripped of its reverse proxy responsibilities. Instead, it operates primarily as a high-speed gRPC server (often deployed as a sidecar or DaemonSet) that evaluates prompts, masks PII, detects jailbreaks, and enforces corporate policies on behalf of the Inference Control Plane.

## 1. Folder Structure

```text
guardrailx/
├── app/
│   ├── api/
│   │   ├── grpc/
│   │   │   ├── server.py
│   │   │   └── services.py
│   │   └── rest/
│   │       ├── dependencies.py
│   │       └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   └── telemetry.py
│   ├── db/
│   │   ├── models.py
│   │   └── repository.py
│   ├── engine/
│   │   ├── evaluator.py
│   │   ├── scanners/
│   │   │   ├── pii.py
│   │   │   ├── toxicity.py
│   │   │   ├── jailbreak.py
│   │   │   └── relevance.py
│   │   └── rules.py
│   ├── proto/
│   │   ├── guardrailx.proto
│   │   └── generated/
│   └── schemas/
│       └── policy.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── deploy/
│   ├── Dockerfile
│   └── kubernetes/
│       └── daemonset.yaml
├── pyproject.toml
└── README.md
```

## 2. Package Structure

- **`app.api.grpc`**: High-performance gRPC server implementation handling `EvaluatePrompt` and `EvaluateResponse` RPCs.
- **`app.api.rest`**: Management REST API for administrators to configure policies, rules, and view violation logs.
- **`app.core`**: OpenTelemetry integration and application configuration.
- **`app.db`**: Data access layer for retrieving policy configurations and storing audit logs.
- **`app.engine`**: The core policy evaluation engine. Coordinates various scanners and aggregates their results.
- **`app.engine.scanners`**: Pluggable modules for specific detection tasks (e.g., regex-based PII, ML-based toxicity or jailbreak detection).
- **`app.proto`**: Protocol Buffer definitions and generated Python code for the gRPC interface.

## 3. Interfaces

- **Inference Control Plane (gRPC)**: Extremely low-latency synchronous interface for evaluating streaming chunks, full prompts, and full responses.
- **Admin Interface (HTTP/REST)**: For updating tenant-specific policies and retrieving audit logs.

## 4. Domain Model

- **Policy**: A collection of rules assigned to a specific Tenant or App ID.
- **Rule**: A specific validation check (e.g., "Block SSN", "Detect Prompt Injection").
- **ScanResult**: The outcome of a single rule check (Pass/Fail/Masked).
- **EvaluationDecision**: The final aggregate decision for a request (Allow, Block, Mask, Flag).
- **AuditLog**: A permanent record of a triggered policy violation.

## 5. API Specification

**gRPC Service: `PolicyService`**

- `rpc EvaluatePrompt (EvaluateRequest) returns (EvaluateResponse)`
- `rpc EvaluateResponse (EvaluateRequest) returns (EvaluateResponse)`

*Message Schema:*
```protobuf
message EvaluateRequest {
  string tenant_id = 1;
  string text_content = 2;
  map<string, string> metadata = 3;
}

message EvaluateResponse {
  enum Decision { ALLOW = 0; BLOCK = 1; MASK = 2; FLAG = 3; }
  Decision decision = 1;
  string modified_text = 2; // e.g., PII redacted text
  repeated string triggered_rules = 3;
}
```

**REST API (Management)**

- `GET /api/v1/policies`: List policies.
- `POST /api/v1/policies`: Create a new policy.
- `GET /api/v1/audit`: Retrieve violation logs.

## 6. Database Schema (PostgreSQL)

- **`policies`**: `id`, `tenant_id`, `name`, `is_active`, `created_at`
- **`rules`**: `id`, `policy_id`, `scanner_type`, `configuration_json`, `action` (block/mask/flag)
- **`audit_logs`**: `id`, `tenant_id`, `request_id`, `timestamp`, `triggered_rule_id`, `original_text`, `decision`

## 7. Event Model

GuardrailX is primarily synchronous on the hot path. However, it can emit asynchronous events for auditing:

- **Subscribes**: None.
- **Publishes**: `security.policy.violated` (to a Kafka/NATS topic or directly to telemetry) for alerting SOC teams without blocking the response.

## 8. Deployment Model

- **Data Plane (Evaluator)**: Deployed as a **DaemonSet** or **Sidecar** alongside the Inference Control Plane to minimize network latency for gRPC calls.
- **Control Plane (Management API)**: Deployed as a standard stateless Deployment.
- **Compute Constraints**: May require small GPUs if utilizing ML-based scanners (e.g., local BERT models for prompt injection detection), otherwise optimized for CPU.

## 9. Testing Strategy

- **Unit Tests**: Test individual scanners (regex accuracy, threshold logic) in isolation.
- **Integration Tests**: Test the gRPC server and ensure the evaluator correctly aggregates multiple scanner results.
- **Performance Benchmarking**: Microbenchmarks on the gRPC endpoints to ensure p99 latency remains under 5-10ms for standard text payloads.

## 10. Roadmap

1.  **Phase 1**: Define Protobuf contracts and implement the gRPC server with basic regex-based PII scanners.
2.  **Phase 2**: Build the evaluation engine to handle complex rule sets and aggregate decisions (Allow/Block/Mask).
3.  **Phase 3**: Implement the Management REST API and database integration for dynamic policy configuration.
4.  **Phase 4**: Integrate ML-based scanners for jailbreak and prompt injection detection.
5.  **Phase 5**: Optimize performance for high-throughput streaming evaluation (evaluating text chunks on the fly).
