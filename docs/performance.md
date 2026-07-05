# Performance

- **Caching**: The Inference Control Plane uses Redis for distributed prompt caching.
- **Scaling**: Scaling is driven by queue depths monitored by the AI Hypervisor Platform, not just CPU.
