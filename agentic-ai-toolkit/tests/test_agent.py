from agentic_toolkit.agent import (
    ReActAgent,
    TrajectoryStep,
    evaluate_trajectory,
    parse_action,
)
from agentic_toolkit.providers import RuleBasedLLM, ScriptedLLM


def test_parse_action():
    assert parse_action("FINAL: hi")[0] == "final"
    kind, tool, args = parse_action('ACTION: calculator {"expression": "1+1"}')
    assert kind == "action" and tool == "calculator" and args["expression"] == "1+1"


def test_parse_action_graceful_fallback():
    kind, text, _ = parse_action("just some prose")
    assert kind == "final" and text == "just some prose"


def test_agent_uses_tool_then_answers():
    llm = ScriptedLLM(
        responses=[
            'ACTION: calculator {"expression": "21 * 2"}',
            "FINAL: The answer is 42.",
        ]
    )
    state = ReActAgent(provider=llm).run("what is 21 * 2?")
    assert state.finished
    assert state.answer == "The answer is 42."
    assert [s.tool for s in state.trajectory] == ["calculator"]
    assert state.trajectory[0].observation == "42"


def test_agent_rule_based_end_to_end():
    state = ReActAgent(provider=RuleBasedLLM()).run("what is 10 + 5?")
    assert "15" in (state.answer or "")
    assert state.trajectory[0].tool == "calculator"


def test_step_budget_is_enforced():
    llm = ScriptedLLM(responses=['ACTION: calculator {"expression": "1+1"}'] * 50)
    state = ReActAgent(provider=llm, max_steps=3).run("loop forever")
    assert state.finished
    assert state.steps <= 3


def test_tool_error_becomes_observation():
    llm = ScriptedLLM(
        responses=[
            'ACTION: calculator {"expression": "oops"}',
            "FINAL: done",
        ]
    )
    state = ReActAgent(provider=llm).run("break it")
    assert state.trajectory[0].observation.startswith("ERROR:")
    assert state.answer == "done"


def test_evaluate_trajectory():
    traj = [TrajectoryStep("calculator", {}, "42")]
    r = evaluate_trajectory(traj, ["calculator"])
    assert r["coverage"] == 1.0 and r["ordered_match"]
    miss = evaluate_trajectory(traj, ["lookup"])
    assert miss["coverage"] == 0.0 and not miss["ordered_match"]
