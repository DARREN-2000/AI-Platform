from typing import Protocol, Any, Dict, List
from intentgraph.models import GraphData

class GraphExecutor(Protocol):
    """
    Protocol defining the contract for a graph execution engine.
    """
    def run(self, graph: GraphData, **kwargs: Any) -> Any:
        ...

class LLMClient(Protocol):
    """
    Protocol defining the contract for executing LLM calls via the Inference Control Plane.
    """
    def generate(self, prompt: str, **kwargs: Any) -> str:
        ...

class RetrievalClient(Protocol):
    """
    Protocol defining the contract for querying EnterpriseIQ context.
    """
    def retrieve(self, query: str, user_jwt: str, **kwargs: Any) -> List[Dict[str, Any]]:
        ...
