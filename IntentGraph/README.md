# IntentGraph

IntentGraph is a pure Python dependency graph and orchestration engine for the Enterprise AI Platform.

It parses Python codebases into a structured dependency graph of files, classes, functions, and imports using AST (Abstract Syntax Tree) parsing, and orchestrates actions using this parsed representation.

## Features

- AST-based parsing of Python files.
- Cross-file dependency tracking (imports, function calls, class definitions).
- Directed graph construction using NetworkX.
- Exporting graph data to structured Pydantic models.
- Pluggable orchestration for multi-agent workflows.

## Usage

```bash
# Example
from intentgraph.builder import GraphBuilder
from intentgraph.orchestrator import Orchestrator
from intentgraph.interfaces import GraphExecutor

builder = GraphBuilder()
graph_data = builder.process_directory("./my_project")

class MyExecutor(GraphExecutor):
    def run(self, graph, **kwargs):
        return {"status": "success", "executed_nodes": len(graph.nodes)}

orchestrator = Orchestrator(MyExecutor())
orchestrator.run(graph_data)
```
