from intentgraph.models import GraphData, Node, Edge
from intentgraph.orchestrator import Orchestrator
from intentgraph.interfaces import GraphExecutor
from typing import Any

class MockExecutor(GraphExecutor):
    def run(self, graph: GraphData, **kwargs: Any) -> Any:
        return {"status": "success", "executed_nodes": len(graph.nodes)}

def test_orchestrator_execution():
    graph_data = GraphData(
        nodes=[
            Node(id="file_1.py", name="file_1.py", type="file", filepath="/tmp/file_1.py"),
            Node(id="func_A", name="func_A", type="function", filepath="/tmp/file_1.py"),
        ],
        edges=[
            Edge(source="file_1.py", target="func_A", type="contains")
        ]
    )

    executor = MockExecutor()
    orchestrator = Orchestrator(executor)
    result = orchestrator.run(graph_data)

    assert result["status"] == "success"
    assert result["executed_nodes"] == 2
