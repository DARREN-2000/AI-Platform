from agentic_toolkit.tracing import Tracer, traced


def test_nested_spans_export_tree():
    t = Tracer()
    with t.span("root", {"k": 1}):
        with t.span("child"):
            pass
    tree = t.export()
    assert tree["name"] == "root"
    assert tree["attributes"]["k"] == 1
    assert len(tree["children"]) == 1
    assert tree["children"][0]["name"] == "child"


def test_traced_decorator():
    t = Tracer()

    @traced(t, "work")
    def work(x):
        return x * 2

    assert work(3) == 6
    assert t.export()["name"] == "work"


def test_multiple_top_level_spans_wrap_in_trace():
    t = Tracer()
    with t.span("a"):
        pass
    with t.span("b"):
        pass
    tree = t.export()
    assert tree["name"] == "trace"
    assert len(tree["children"]) == 2
    assert {c["name"] for c in tree["children"]} == {"a", "b"}
