import networkx as nx
from typing import List, Dict, Any
from intentgraph.models import GraphData, Node, Edge

class DependencyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_nodes(self, nodes: List[Dict[str, Any]]):
        for node in nodes:
            self.graph.add_node(
                node["id"],
                name=node.get("name", ""),
                type=node.get("type", ""),
                filepath=node.get("filepath", "")
            )

    def add_edges(self, edges: List[Dict[str, Any]]):
        for edge in edges:
            self.graph.add_edge(
                edge["source"],
                edge["target"],
                type=edge.get("type", "")
            )

    def export_to_pydantic(self) -> GraphData:
        nodes = []
        for n_id, data in self.graph.nodes(data=True):
            nodes.append(Node(
                id=n_id,
                name=data.get("name", ""),
                type=data.get("type", ""),
                filepath=data.get("filepath", "")
            ))

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append(Edge(
                source=u,
                target=v,
                type=data.get("type", "")
            ))

        return GraphData(nodes=nodes, edges=edges)
