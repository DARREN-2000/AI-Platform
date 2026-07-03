import tempfile
import os
from intentgraph.builder import GraphBuilder
from intentgraph.orchestrator import Orchestrator
from intentgraph.interfaces import GraphExecutor

class DummyExecutor(GraphExecutor):
    def run(self, graph, **kwargs):
        return {"status": "success", "executed_nodes": len(graph.nodes)}

def test_full_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy python file
        test_file_path = os.path.join(tmpdir, "test_dummy.py")
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("""
def hello():
    print("Hello, world!")

class Greeter:
    def greet(self):
        hello()
""")

        # Build graph
        builder = GraphBuilder()
        graph_data = builder.process_directory(tmpdir)

        # Assert graph has nodes
        assert len(graph_data.nodes) > 0

        # Orchestrate
        executor = DummyExecutor()
        orchestrator = Orchestrator(executor)
        result = orchestrator.run(graph_data)

        # Assert result
        assert result["status"] == "success"
        assert result["executed_nodes"] == len(graph_data.nodes)
