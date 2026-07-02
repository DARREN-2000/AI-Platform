from typing import List
from pydantic import BaseModel

class Node(BaseModel):
    id: str
    name: str
    type: str
    filepath: str

class Edge(BaseModel):
    source: str
    target: str
    type: str

class GraphData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
