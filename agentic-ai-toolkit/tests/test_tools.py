import pytest

from agentic_toolkit.tools import default_registry, safe_arith


def test_safe_arith():
    assert safe_arith("21 * 2") == 42
    assert safe_arith("(2 + 3) * 4") == 20
    assert safe_arith("-5 + 2") == -3


def test_safe_arith_rejects_names():
    with pytest.raises(ValueError):
        safe_arith("__import__('os')")


def test_calculator_tool():
    reg = default_registry()
    assert reg.run("calculator", {"expression": "6 / 2"}) == "3.0"


def test_lookup_tool():
    reg = default_registry()
    assert "Paris" in reg.run("lookup", {"key": "France"})
    assert reg.run("lookup", {"key": "nowhere"}) == "No entry found."


def test_unknown_tool_raises():
    reg = default_registry()
    with pytest.raises(KeyError):
        reg.run("nope", {})
