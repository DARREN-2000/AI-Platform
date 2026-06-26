# 22 — Repository Templates

MUST adapt these structures to the task; MUST NOT create empty folders for layers the task does not need.

## FastAPI service
```
repo/
  src/app/{api,services,domain,db,core,config.py,main.py}
  tests/{unit,integration}
  Dockerfile  docker-compose.yml  pyproject.toml  .env.example
  .github/workflows/ci.yml  README.md
```

## Python package / library
```
repo/
  src/<pkg>/{__init__.py,...}
  tests/
  pyproject.toml  README.md  CHANGELOG.md
  .github/workflows/ci.yml
```

## CLI
```
repo/
  src/<cli>/{__main__.py,cli.py,commands/,core/}
  tests/
  pyproject.toml  README.md
```

## Microservice
```
repo/
  src/app/{api,domain,infra,config.py,main.py}
  migrations/
  tests/{unit,integration}
  Dockerfile  docker-compose.yml  .env.example
  .github/workflows/ci.yml  README.md
```

## AI agent
```
repo/
  src/app/{agent/{graph,nodes,state.py},tools/,llm/,prompts/,eval/,observability/,config.py}
  data/golden/*.jsonl
  tests/{unit,integration,eval}
  Dockerfile  docker-compose.yml  .env.example
  .github/workflows/ci.yml  README.md
```

## Worker / consumer
```
repo/
  src/app/{handlers/,core/,config.py,main.py}
  tests/
  Dockerfile  .env.example
  .github/workflows/ci.yml  README.md
```

## Rules
- MUST place `.ai/` rule files and root `CLAUDE.md` + `AGENTS.md` in every repo.
- MUST include `.gitignore`, `.dockerignore`, `.env.example`, lockfile, and CI.
- SHOULD keep `src/` import-safe and tests mirroring the source layout.
