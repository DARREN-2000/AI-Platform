# 17 — GitHub & Git

## Branches & commits
- MUST use short-lived feature branches off `main`; MUST NOT commit broken code to `main`.
- MUST write small, focused commits with conventional commit messages.
- MUST NOT commit secrets, large binaries, or generated artifacts.

## Pull requests
- MUST keep PRs small and single-purpose; large PRs MUST be split.
- MUST describe what changed, why, and how to test; MUST link the issue.
- MUST pass all required CI checks before merge; MUST resolve all review threads.
- SHOULD request review and self-review against `19-review.md` first.

## Branch protection
- SHOULD protect `main`: required status checks, required review, no force-push.
- MUST require the eval gate to pass for changes touching AI behavior.

## GitHub Actions
- MUST pin action versions; SHOULD pin by commit SHA for third-party actions.
- MUST scope `GITHUB_TOKEN`/workflow permissions to least privilege (`permissions:` block).
- MUST store secrets in GitHub Secrets; MUST NOT echo secrets into logs.
- SHOULD cache dependencies and fail fast on lint/type/test/eval steps.
