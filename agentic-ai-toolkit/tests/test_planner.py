from agentic_toolkit.planner import PlanAndExecuteAgent, parse_plan
from agentic_toolkit.providers import ScriptedLLM


def test_parse_plan_numbered_and_bullets():
    assert parse_plan("1. a\n2) b\n- c\n* d\nnoise") == ["a", "b", "c", "d"]


def test_plan_and_execute_threads_steps():
    prov = ScriptedLLM(responses=[
        "1. first\n2. second",
        "FINAL: r1",
        "FINAL: r2",
    ])
    agent = PlanAndExecuteAgent(provider=prov)
    res = agent.execute("do the thing")
    assert res.plan == ["first", "second"]
    assert [s.result for s in res.steps] == ["r1", "r2"]
    assert res.answer == "r2"


def test_plan_falls_back_to_whole_task():
    prov = ScriptedLLM(responses=["no list here", "FINAL: done"])
    agent = PlanAndExecuteAgent(provider=prov)
    res = agent.execute("solve")
    assert res.plan == ["solve"]
    assert res.answer == "done"
