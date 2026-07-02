from intentgraph.graph import DependencyGraph

def test_dependency_graph():
    graph = DependencyGraph()

    nodes = [
        {"id": "file1.py", "name": "file1.py", "type": "file", "filepath": "file1.py"},
        {"id": "func1", "name": "func1", "type": "function", "filepath": "file1.py"}
    ]
    edges = [
        {"source": "file1.py", "target": "func1", "type": "contains"}
    ]

    graph.add_nodes(nodes)
    graph.add_edges(edges)

    pydantic_graph = graph.export_to_pydantic()

    assert len(pydantic_graph.nodes) == 2
    assert len(pydantic_graph.edges) == 1

    assert pydantic_graph.nodes[0].id in ["file1.py", "func1"]
    assert pydantic_graph.edges[0].source == "file1.py"
    assert pydantic_graph.edges[0].target == "func1"
    assert pydantic_graph.edges[0].type == "contains"
