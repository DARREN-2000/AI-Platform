from agentic_toolkit.memory import (
    BufferMemory,
    SummarizingMemory,
    TokenWindowMemory,
    WindowMemory,
)
from agentic_toolkit.providers import ScriptedLLM


def test_buffer_keeps_all_and_system():
    m = BufferMemory(system="sys")
    m.add_user("a").add_assistant("b")
    h = m.history()
    assert h[0].role == "system" and h[0].content == "sys"
    assert [x.content for x in h[1:]] == ["a", "b"]


def test_window_keeps_last_n():
    m = WindowMemory(max_messages=2)
    for i in range(5):
        m.add_user(str(i))
    assert [x.content for x in m.history()] == ["3", "4"]


def test_token_window_respects_budget():
    m = TokenWindowMemory(max_tokens=2)
    for _ in range(5):
        m.add_user("wxyz")  # ~1 estimated token each
    assert len(m.history()) == 2


def test_summarizing_compresses_overflow_offline():
    m = SummarizingMemory(max_messages=2)  # no provider -> deterministic
    for i in range(5):
        m.add_user(f"msg{i}")
    assert m.summary
    assert len(m.messages) == 2
    hist = m.history()
    assert hist[0].role == "system" and "Summary so far" in hist[0].content


def test_summarizing_uses_provider():
    prov = ScriptedLLM(responses=["SUM1", "SUM2", "SUM3"])
    m = SummarizingMemory(max_messages=2, provider=prov)
    for i in range(4):
        m.add_user(f"m{i}")
    assert m.summary in {"SUM1", "SUM2", "SUM3"}
