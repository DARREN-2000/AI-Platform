import pytest

from agentic_toolkit.prompts import PromptLibrary, PromptTemplate


def test_variables_and_render():
    t = PromptTemplate("greet", "Hello {name}, you are {role}.")
    assert t.variables() == ["name", "role"]
    assert t.render(name="Ada", role="dev") == "Hello Ada, you are dev."


def test_missing_variable_raises():
    t = PromptTemplate("greet", "Hi {name}")
    with pytest.raises(KeyError):
        t.render()


def test_library_versioning():
    lib = PromptLibrary()
    lib.register(PromptTemplate("judge", "v1 {x}", version=1))
    lib.register(PromptTemplate("judge", "v2 {x}", version=2))
    assert lib.get("judge").version == 2  # latest by default
    assert lib.get("judge", 1).template == "v1 {x}"
    assert lib.render("judge", x="!") == "v2 !"
    assert lib.versions("judge") == [1, 2]
