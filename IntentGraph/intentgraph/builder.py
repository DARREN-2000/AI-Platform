import os
from typing import List, Optional

from intentgraph.parser import CodeParser
from intentgraph.graph import DependencyGraph
from intentgraph.models import GraphData
from intentgraph.logger import setup_logger

logger = setup_logger(__name__)

class GraphBuilder:
    def __init__(self) -> None:
        self.parser = CodeParser()
        self.graph = DependencyGraph()

    def process_directory(self, directory: str, exclude_dirs: Optional[List[str]] = None) -> GraphData:
        """Processes a directory to build a full cross-file dependency graph."""
        if exclude_dirs is None:
            exclude_dirs = [".git", "__pycache__", "venv", ".venv", "node_modules", "dist", "build"]

        logger.info(f"Starting analysis of directory: {directory}")

        python_files: List[str] = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        logger.info(f"Found {len(python_files)} Python files to parse.")

        for filepath in python_files:
            logger.debug(f"Parsing file: {filepath}")
            nodes, edges = self.parser.parse_file(filepath)
            self.graph.add_nodes(nodes)
            self.graph.add_edges(edges)

        logger.info("Finished parsing and building the graph.")
        return self.graph.export_to_pydantic()
