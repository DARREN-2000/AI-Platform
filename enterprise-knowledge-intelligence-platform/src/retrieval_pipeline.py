from src import config
from src.retrieval.hybrid_retriever import HybridRetriever, RetrievalRequest
from src.retrieval.query_router import QueryRouter
from src.security.audit import AuditLogger
from src.security.rbac import RBACEngine
from src.api.models import QueryResponse

class RetrievalPipeline:
    def __init__(self, retriever: HybridRetriever, rbac: RBACEngine, router: QueryRouter, audit: AuditLogger):
        self.retriever = retriever
        self.rbac = rbac
        self.router = router
        self.audit = audit

    def query(
        self, query: str, role: str | None = None, user_id: str = "", top_k: int | None = None
    ) -> QueryResponse:
        eff_role = self.rbac.resolve_role(user_id or None, role)
        route = self.router.classify(query)

        request = RetrievalRequest(
            query=query,
            role=eff_role,
            route=route,
            top_k=(top_k or config.TOP_K) * 2,
            user_id=user_id,
        )
        chunks, decisions = self.retriever.retrieve(request)

        denied = sum(1 for d in decisions if not d.allowed)
        authorised = sum(1 for d in decisions if d.allowed)

        self.audit.log_query(
            user_id or eff_role,
            eff_role,
            query,
            authorised=authorised,
            denied=denied,
            confidence=1.0,
        )
        self.audit.log_access_decisions(user_id or eff_role, eff_role, decisions)

        return QueryResponse(
            query=query,
            role=eff_role,
            user_id=user_id,
            answer="",
            confidence={"score": 1.0, "level": "high", "factors": []},
            citations=[],
            route=route.to_dict(),
            coverage={},
            access_decisions=decisions,
            authorised_count=authorised,
            denied_count=denied,
        )
