from typing import Any
from intentgraph.models import GraphData
from intentgraph.interfaces import GraphExecutor
from intentgraph.logger import setup_logger

logger = setup_logger(__name__)

class Orchestrator:
    def __init__(self, executor: GraphExecutor) -> None:
        self.executor = executor

    def run(self, graph: GraphData, **kwargs: Any) -> Any:
        """Executes actions based on the provided GraphData using the injected executor."""
        logger.info(f"Orchestrator delegating execution on graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges.")
        return self.executor.run(graph, **kwargs)
