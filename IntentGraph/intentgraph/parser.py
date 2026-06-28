import ast
import logging
from typing import Tuple, List, Dict, Any
from intentgraph.logger import setup_logger

logger = setup_logger(__name__)

class CodeParser:
    def __init__(self):
        pass

    def parse_file(self, filepath: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        nodes = []
        edges = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=filepath)
        except Exception as e:
            logger.warning(f"Failed to parse {filepath}: {e}")
            return [], []

        file_id = filepath
        nodes.append({
            "id": file_id,
            "name": filepath.split("/")[-1],
            "type": "file",
            "filepath": filepath
        })

        class DependencyVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_class = None
                self.current_function = None

            def visit_ClassDef(self, node):
                class_id = f"{filepath}::{node.name}"
                nodes.append({
                    "id": class_id,
                    "name": node.name,
                    "type": "class",
                    "filepath": filepath
                })
                edges.append({
                    "source": file_id,
                    "target": class_id,
                    "type": "contains"
                })

                for base in node.bases:
                    if isinstance(base, ast.Name):
                        edges.append({
                            "source": class_id,
                            "target": base.id, # We might not know the exact file of the base class
                            "type": "inherits"
                        })

                old_class = self.current_class
                self.current_class = class_id
                self.generic_visit(node)
                self.current_class = old_class

            def visit_FunctionDef(self, node):
                func_id = f"{filepath}::{node.name}"
                if self.current_class:
                    func_id = f"{self.current_class}.{node.name}"

                nodes.append({
                    "id": func_id,
                    "name": node.name,
                    "type": "function",
                    "filepath": filepath
                })

                parent_id = self.current_class if self.current_class else file_id
                edges.append({
                    "source": parent_id,
                    "target": func_id,
                    "type": "contains"
                })

                old_function = self.current_function
                self.current_function = func_id
                self.generic_visit(node)
                self.current_function = old_function

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    if self.current_function:
                        edges.append({
                            "source": self.current_function,
                            "target": node.func.id, # Call to another function
                            "type": "calls"
                        })
                elif isinstance(node.func, ast.Attribute):
                    if self.current_function:
                        edges.append({
                            "source": self.current_function,
                            "target": node.func.attr,
                            "type": "calls"
                        })
                self.generic_visit(node)

            def visit_Import(self, node):
                for alias in node.names:
                    nodes.append({
                        "id": f"module::{alias.name}",
                        "name": alias.name,
                        "type": "module",
                        "filepath": ""
                    })
                    edges.append({
                        "source": file_id,
                        "target": f"module::{alias.name}",
                        "type": "imports"
                    })
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                for alias in node.names:
                    full_name = f"{node.module}.{alias.name}" if node.module else alias.name
                    nodes.append({
                        "id": f"module::{full_name}",
                        "name": full_name,
                        "type": "module",
                        "filepath": ""
                    })
                    edges.append({
                        "source": file_id,
                        "target": f"module::{full_name}",
                        "type": "imports"
                    })
                self.generic_visit(node)

        visitor = DependencyVisitor()
        visitor.visit(tree)

        return nodes, edges
