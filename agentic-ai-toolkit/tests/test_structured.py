import pytest

from agentic_toolkit.providers import Message, ScriptedLLM
from agentic_toolkit.structured import (
    SchemaError,
    extract_json,
    generate_structured,
    validate,
)

SCHEMA = {
    "type": "object",
    "required": ["score", "label"],
    "properties": {
        "score": {"type": "integer", "minimum": 1, "maximum": 5},
        "label": {"type": "string", "enum": ["good", "bad"]},
    },
}


def test_extract_json_from_fence():
    assert extract_json('here:\n```json\n{"a": 1}\n```\nthanks') == {"a": 1}


def test_extract_json_from_prose():
    obj = extract_json('The verdict is {"score": 5, "label": "good"} ok')
    assert obj["score"] == 5


def test_extract_json_raises_when_absent():
    with pytest.raises(SchemaError):
        extract_json("no json here")


def test_validate_accepts_valid():
    validate({"score": 4, "label": "good"}, SCHEMA)


def test_validate_rejects_missing_required():
    with pytest.raises(SchemaError):
        validate({"score": 4}, SCHEMA)


def test_validate_rejects_bad_enum():
    with pytest.raises(SchemaError):
        validate({"score": 4, "label": "meh"}, SCHEMA)


def test_validate_rejects_out_of_range():
    with pytest.raises(SchemaError):
        validate({"score": 9, "label": "good"}, SCHEMA)


def test_validate_rejects_bool_as_integer():
    with pytest.raises(SchemaError):
        validate({"score": True, "label": "good"}, SCHEMA)


def test_generate_structured_repairs_then_succeeds():
    provider = ScriptedLLM(responses=["oops not json", '{"score": 5, "label": "good"}'])
    obj = generate_structured(provider, [Message("user", "judge it")], SCHEMA, retries=2)
    assert obj == {"score": 5, "label": "good"}


def test_generate_structured_raises_after_retries():
    provider = ScriptedLLM(responses=["nope", "still nope", "nada"])
    with pytest.raises(SchemaError):
        generate_structured(provider, [Message("user", "x")], SCHEMA, retries=2)
