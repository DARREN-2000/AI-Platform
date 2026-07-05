# Architecture

The platform is designed as a distributed, microservices-based system avoiding a monolithic structure. It is composed of five bounded contexts.

## Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant IntentGraph
    participant EnterpriseIQ
    participant InferenceControlPlane
    participant GuardrailX
    participant AIHypervisorPlatform

    User->>IntentGraph: Submit Intent (User JWT)
    IntentGraph->>EnterpriseIQ: /retrieve (Forward JWT)
    EnterpriseIQ-->>IntentGraph: Context Chunks + Citations
    IntentGraph->>InferenceControlPlane: /chat/completions (Prompt + Context)
    InferenceControlPlane->>GuardrailX: gRPC: Evaluate Request
    GuardrailX-->>InferenceControlPlane: Approved / Redacted
    InferenceControlPlane->>InferenceControlPlane: Route to Target Model
    InferenceControlPlane--)AIHypervisorPlatform: Emit Queue Depth Metrics (NATS)
    InferenceControlPlane-->>IntentGraph: Stream Response
    IntentGraph-->>User: Final Output
```

See [Design](design.md) for more details.
