# 10 — Security

## Secrets
- MUST NOT hardcode or commit secrets, tokens, or credentials.
- MUST load secrets from env/secret manager; MUST keep `.env` out of git.
- MUST scan diffs for secrets before commit; MUST rotate any leaked secret.

## Input & output
- MUST validate and sanitize all external input at the boundary.
- MUST use parameterized queries; MUST NOT build SQL/commands by string concatenation.
- MUST encode/escape output to prevent injection (SQL, shell, XSS, prompt).
- MUST treat all LLM output and tool results as untrusted input.

## AuthN / AuthZ
- MUST authenticate before authorizing; MUST enforce least privilege.
- MUST check authorization on every protected operation, server-side.
- MUST NOT trust client-supplied identity, roles, or prices.

## Transport & storage
- MUST use TLS for all network calls; MUST NOT disable certificate verification.
- MUST hash passwords with a strong adaptive algorithm; MUST encrypt sensitive data at rest.
- MUST set timeouts and size limits on all inbound/outbound requests.

## Dependencies & supply chain
- MUST pin versions and run dependency vulnerability scanning in CI.
- MUST run containers as a non-root user with a minimal base image.
- SHOULD apply least-privilege IAM and drop unused capabilities.

## Logging
- MUST NOT log secrets, tokens, full PII, or full prompts containing sensitive data.
- SHOULD redact sensitive fields centrally.
