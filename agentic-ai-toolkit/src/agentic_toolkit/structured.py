"""Structured output: pull JSON from model text and validate it against a tiny
JSON-Schema subset, with an optional self-repair loop.

Production agents need *typed* outputs, not prose. Models drift (code fences,
trailing text, a wrong field). ``generate_structured`` re-prompts with the exact
validation error so the model can fix itself - the same pattern behind OpenAI
function-calling / ``response_format``, implemented dependency-free.
"""
from __future__ import annotations

import json
import re
from typing import Any, List, Optional, Sequence

from .providers import Message, Provider


class SchemaError(ValueError):
    """Raised when text has no JSON or the JSON violates the schema."""


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _first_json_span(text: str) -> Optional[str]:
    """Return the first balanced {...}/[...] span, ignoring brackets in strings."""
    start = None
    for i, ch in enumerate(text):
        if ch in "{[":
            start = i
            break
    if start is None:
        return None
    depth = 0
    in_str = False
    esc = False
    for j in range(start, len(text)):
        ch = text[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
            if depth == 0:
                return text[start : j + 1]
    return None


def extract_json(text: str) -> Any:
    """Extract the first JSON value from model output, tolerating ```json fences
    and surrounding prose."""
    if not text:
        raise SchemaError("no text to parse")
    candidates: List[str] = []
    fence = _FENCE.search(text)
    if fence:
        candidates.append(fence.group(1).strip())
    candidates.append(text.strip())
    span = _first_json_span(text)
    if span:
        candidates.append(span)
    for cand in candidates:
        try:
            return json.loads(cand)
        except (json.JSONDecodeError, TypeError):
            continue
    raise SchemaError(f"no valid JSON found in: {text[:120]!r}")


_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


def validate(instance: Any, schema: dict, *, path: str = "$") -> None:
    """Validate ``instance`` against a JSON-Schema subset. Raises ``SchemaError``.

    Supported keywords: type, enum, required, properties, items, minimum,
    maximum, minLength, maxLength, minItems, maxItems. Unknown keywords are
    ignored (forward-compatible).
    """
    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(f"{path}: {instance!r} not in enum {schema['enum']}")
    t = schema.get("type")
    if t:
        expected = _TYPES.get(t)
        if expected is None:
            raise SchemaError(f"{path}: unknown type {t!r} in schema")
        # bool is a subclass of int; reject it where number/integer is expected.
        if t in ("number", "integer") and isinstance(instance, bool):
            raise SchemaError(f"{path}: expected {t}, got boolean")
        if not isinstance(instance, expected):
            raise SchemaError(f"{path}: expected {t}, got {type(instance).__name__}")
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise SchemaError(f"{path}: shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            raise SchemaError(f"{path}: longer than maxLength {schema['maxLength']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            raise SchemaError(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            raise SchemaError(f"{path}: {instance} > maximum {schema['maximum']}")
    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                raise SchemaError(f"{path}: missing required property {req!r}")
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                validate(instance[key], subschema, path=f"{path}.{key}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise SchemaError(f"{path}: fewer than minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            raise SchemaError(f"{path}: more than maxItems {schema['maxItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for idx, item in enumerate(instance):
                validate(item, item_schema, path=f"{path}[{idx}]")


def parse_structured(text: str, schema: dict) -> Any:
    """Extract JSON from text and validate it against the schema."""
    obj = extract_json(text)
    validate(obj, schema)
    return obj


def generate_structured(
    provider: Provider,
    messages: Sequence[Message],
    schema: dict,
    *,
    retries: int = 2,
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> Any:
    """Call the provider and return validated JSON, re-prompting with the exact
    error on failure (up to ``retries`` repairs)."""
    convo = list(messages)
    last_err = ""
    for _ in range(max(1, retries + 1)):
        raw = provider.complete(convo, temperature=temperature, max_tokens=max_tokens)
        try:
            return parse_structured(raw, schema)
        except SchemaError as exc:
            last_err = str(exc)
            convo = convo + [
                Message("assistant", raw),
                Message(
                    "user",
                    "Your previous output was invalid: "
                    f"{last_err}. Return ONLY JSON matching this schema: "
                    f"{json.dumps(schema)}",
                ),
            ]
    raise SchemaError(f"failed after retries; last error: {last_err}")
