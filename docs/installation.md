# Installation Guide

The platform is designed to be deployed via Docker Compose for local development and Kubernetes for production.

## Local Development (Docker Compose)

Currently, individual services can be started independently. A unified `docker-compose.yml` is on the roadmap.

To run the frontend dashboard:

```bash
cd dashboard
npm install
npm run build
npm run preview
```

To run a specific service, navigate to its directory and follow its respective README (e.g., `cd IntentGraph` and run `poetry install && poetry run pytest` to verify setup).
