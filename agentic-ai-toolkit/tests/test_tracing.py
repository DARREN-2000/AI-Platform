from agentic_toolkit.tracing import Tracer, to_langfuse, to_langsmith, traced


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


def test_to_langsmith_nested_run_tree():
    t = Tracer()
    with t.span("root"):
        with t.span("child"):
            pass
    ls = to_langsmith(t.export())
    assert ls["run_type"] == "chain"
    assert ls["name"] == "root"
    assert ls["child_runs"][0]["name"] == "child"


def test_to_langfuse_flattens_with_parent_ids():
    t = Tracer()
    with t.span("root"):
        with t.span("child"):
            pass
    lf = to_langfuse(t.export())
    obs = lf["observations"]
    assert len(obs) == 2
    root = next(o for o in obs if o["name"] == "root")
    child = next(o for o in obs if o["name"] == "child")
    assert root["parentObservationId"] is None
    assert child["parentObservationId"] == root["id"]
