# Security Architecture

- **mTLS:** Enforced between all repositories via a Service Mesh.
- **Data Protection:** `GuardrailX` ensures no sensitive PII leaks to external LLM providers.
- **Compute Isolation:** `AI Hypervisor Platform` provides strict multi-tenant isolation at the VM/Hypervisor level when running local models.
