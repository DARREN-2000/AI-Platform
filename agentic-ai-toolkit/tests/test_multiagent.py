from agentic_toolkit.multiagent import (
    NamedAgent,
    Supervisor,
    keyword_router,
    llm_router,
)
from agentic_toolkit.providers import ScriptedLLM


def _agents():
    return [
        NamedAgent("math", "does arithmetic", lambda q: "math:" + q),
        NamedAgent("geo", "geography facts", lambda q: "geo:" + q),
    ]


def test_keyword_routing():
    sup = Supervisor(
        router=keyword_router(
            {"math": ["calculate", "sum"], "geo": ["capital"]}, default="geo"
        )
    )
    for a in _agents():
        sup.register(a)
    out = sup.run("please calculate 2+2")
    assert out["agent"] == "math"
    assert out["answer"] == "math:please calculate 2+2"
    assert sup.run("hello there")["agent"] == "geo"  # default


def test_default_routing_without_router():
    sup = Supervisor()
    sup.register(NamedAgent("only", "the only one", lambda q: "ok"))
    assert sup.run("anything")["agent"] == "only"


def test_llm_routing():
    sup = Supervisor(router=llm_router(ScriptedLLM(responses=["math"]), _agents(), "geo"))
    for a in _agents():
        sup.register(a)
    assert sup.run("2+2?")["agent"] == "math"
