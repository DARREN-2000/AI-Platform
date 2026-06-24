import os

import pytest

from agentic_toolkit.config import DEFAULT_DOCS, build_provider, load_docs
from agentic_toolkit.providers import AnthropicProvider, OpenAIProvider, RuleBasedLLM


def test_default_provider_is_offline():
    assert isinstance(build_provider(), RuleBasedLLM)


def test_named_providers():
    assert isinstance(build_provider("openai"), OpenAIProvider)
    assert isinstance(build_provider("anthropic"), AnthropicProvider)


def test_unknown_provider_raises():
    with pytest.raises(ValueError):
        build_provider("nope")


def test_env_override():
    os.environ["AGENTIC_PROVIDER"] = "openai"
    try:
        assert isinstance(build_provider(), OpenAIProvider)
    finally:
        del os.environ["AGENTIC_PROVIDER"]


def test_load_docs_defaults_without_env():
    os.environ.pop("AGENTIC_DOCS_PATH", None)
    assert load_docs() == DEFAULT_DOCS
