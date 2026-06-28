import os
import tempfile
from intentgraph.parser import CodeParser

def test_code_parser():
    parser = CodeParser()

    source_code = """
import os
from collections import defaultdict

class MyClass(object):
    def my_method(self):
        print("Hello")

def top_level_func():
    m = MyClass()
    m.my_method()
"""

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as f:
        f.write(source_code)
        temp_path = f.name

    try:
        nodes, edges = parser.parse_file(temp_path)

        node_ids = [n["id"] for n in nodes]
        assert temp_path in node_ids
        assert f"{temp_path}::MyClass" in node_ids
        assert f"{temp_path}::MyClass.my_method" in node_ids
        assert f"{temp_path}::top_level_func" in node_ids

        assert "module::os" in node_ids
        assert "module::collections.defaultdict" in node_ids

        edge_tuples = [(e["source"], e["target"], e["type"]) for e in edges]
        assert (temp_path, f"{temp_path}::MyClass", "contains") in edge_tuples
        assert (f"{temp_path}::MyClass", f"{temp_path}::MyClass.my_method", "contains") in edge_tuples
        assert (temp_path, f"{temp_path}::top_level_func", "contains") in edge_tuples

    finally:
        os.remove(temp_path)
