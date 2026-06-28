from typing import Protocol, Any
from intentgraph.models import GraphData

class GraphExecutor(Protocol):
    """
    Protocol defining the contract for a graph execution engine.
    """
    def run(self, graph: GraphData, **kwargs: Any) -> Any:
        ...
