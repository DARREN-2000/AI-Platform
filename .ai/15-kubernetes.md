# 15 — Kubernetes

## Workloads
- MUST define liveness, readiness, and (where useful) startup probes.
- MUST set resource requests and limits for every container.
- MUST pin image tags by digest or immutable version; MUST NOT deploy `latest`.
- MUST run as non-root with a read-only root filesystem where possible and drop unneeded capabilities.

## Config & secrets
- MUST inject config via ConfigMaps and secrets via Secret objects (or an external secret manager).
- MUST NOT bake environment-specific config or secrets into images.

## Reliability
- MUST handle SIGTERM and respect `terminationGracePeriodSeconds` for graceful shutdown.
- SHOULD set PodDisruptionBudgets and multiple replicas for availability.
- SHOULD configure autoscaling (HPA) on meaningful metrics.
- MUST set appropriate rollout strategy and `revisionHistoryLimit` for rollback.

## Networking & policy
- SHOULD apply NetworkPolicies for least-privilege traffic.
- MUST NOT expose internal services publicly without an ingress/auth layer.
