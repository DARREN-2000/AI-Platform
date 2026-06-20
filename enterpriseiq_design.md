# EnterpriseIQ - V2 Architecture Design

EnterpriseIQ is the enterprise knowledge and retrieval engine. In the V2 architecture, all agentic logic, LLM interaction, and answer generation have been completely stripped out. EnterpriseIQ is strictly a data ingestion, embedding, and highly secure hybrid-retrieval engine. It serves context to IntentGraph based on strict Role-Based Access Control (RBAC).

## 1. Folder Structure

```text
enterpriseiq/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── ingestion.py
│   │       ├── retrieval.py
│   │       └── connectors.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   └── vector_store.py
│   ├── ingestion/
│   │   ├── chunkers/
│   │   ├── loaders/
│   │   └── pipeline.py
│   ├── retrieval/
│   │   ├── query_expansion.py
│   │   ├── hybrid_search.py
│   │   └── reranker.py
│   ├── schemas/
│   │   ├── document.py
│   │   └── query.py
│   └── services/
│       ├── indexer.py
│       └── searcher.py
├── tests/
│   ├── unit/
│   └── integration/
├── deploy/
│   └── Dockerfile
├── pyproject.toml
└── README.md
```

## 2. Package Structure

- **`app.api`**: FastAPI routes for managing document ingestion and executing search queries.
- **`app.core.security`**: Crucial module handling JWT validation and extracting RBAC claims for document filtering.
- **`app.db.vector_store`**: Abstraction layer over the vector database (e.g., ChromaDB, Milvus, or pgvector).
- **`app.ingestion`**: Logic for parsing various document types, chunking text, and generating embeddings via the Inference Control Plane.
- **`app.retrieval`**: Implementation of hybrid search (Vector + BM25) and cross-encoder re-ranking.
- **`app.schemas`**: Pydantic models representing documents, chunks, and search results with citation metadata.

## 3. Interfaces

- **IntentGraph (HTTP/REST)**: IntentGraph calls the `/v1/retrieve` endpoint, passing the user's JWT. EnterpriseIQ returns raw text chunks and metadata.
- **Inference Control Plane (HTTP/REST)**: EnterpriseIQ calls the `/v1/embeddings` endpoint to vectorize documents during ingestion and to vectorize the query during retrieval.
- **External Data Sources**: Connectors (APIs, webhooks) to ingest data from SharePoint, Confluence, Jira, etc.

## 4. Domain Model

- **Document**: The original file or web page (e.g., an Employee Handbook PDF).
- **Chunk**: A segment of a Document, associated with a dense vector representation.
- **Metadata**: Key-value pairs attached to a Chunk, crucial for RBAC (e.g., `allowed_roles: ["HR", "Manager"]`).
- **QueryContext**: The parsed search request including the user's identity, roles, and the search text.
- **SearchResult**: A scored and ranked Chunk returned to the caller.

## 5. API Specification

**Base URL**: `/v1`

- `POST /v1/retrieve`: The core search endpoint.
  - *Headers*: `Authorization: Bearer <User_JWT>`
  - *Request*: `{ "query": "What is the new remote work policy?", "top_k": 5 }`
  - *Response*: List of `SearchResult` objects containing `text`, `score`, and `document_metadata`.
- `POST /v1/documents/ingest`: Upload a document or trigger a connector sync.
- `DELETE /v1/documents/{id}`: Remove a document from the index.
- `GET /v1/connectors/status`: Check the status of background ingestion jobs.

## 6. Database Schema

**Vector Database (e.g., pgvector or Milvus)**
- **Collection**: `enterprise_knowledge`
  - `id`: UUID (Chunk ID)
  - `document_id`: UUID
  - `text`: String
  - `embedding`: Vector
  - `metadata`: JSONB (contains `allowed_groups`, `source_url`, `title`)

**Relational Database (PostgreSQL - Optional, for connector state)**
- **`ingestion_jobs`**: `id`, `connector_type`, `status`, `documents_processed`, `started_at`

## 7. Event Model

- **Subscribes**: Can optionally listen to Kafka/NATS events for real-time data ingestion (e.g., `confluence.page.updated`).
- **Publishes**: `knowledge.index.updated` when new documents are successfully vectorized and searchable.

## 8. Deployment Model

- **API Servers**: Stateless FastAPI instances.
- **Workers**: Celery or arq workers for background ingestion and chunking tasks.
- **Storage**: Requires a robust vector database deployment. If using pgvector, it can co-locate with the platform's main PostgreSQL instance or run dedicated.

## 9. Testing Strategy

- **Unit Tests**: Verify chunking algorithms, query expansion logic, and metadata extraction.
- **Integration Tests**: Spin up a local vector DB (e.g., ChromaDB in-memory) to test ingestion and hybrid search pipelines end-to-end.
- **Security Tests**: Crucially, test that queries with specific JWTs *cannot* retrieve documents tagged for higher privilege levels.

## 10. Roadmap

1.  **Phase 1**: Clean up the repository by removing all LLM generation, prompting, and agent logic.
2.  **Phase 2**: Establish the pure `/v1/retrieve` endpoint and implement JWT parsing for RBAC metadata filtering.
3.  **Phase 3**: Implement hybrid search (Dense Vector + Sparse/BM25).
4.  **Phase 4**: Add a dedicated re-ranking step (e.g., Cohere Rerank or local cross-encoder) to improve retrieval precision.
5.  **Phase 5**: Develop robust ingestion connectors for common enterprise systems.
