from agentic_toolkit.providers import Message, ScriptedLLM
from agentic_toolkit.streaming import StreamingProvider, collect, word_stream


def test_word_stream_roundtrip():
    text = "hello   world\nfoo"
    assert collect(word_stream(text)) == text


def test_streaming_provider_streams():
    prov = StreamingProvider(ScriptedLLM(responses=["one two three"]))
    chunks = list(prov.stream([Message("user", "hi")]))
    assert collect(chunks) == "one two three"
    assert len(chunks) > 1


def test_streaming_provider_name():
    prov = StreamingProvider(ScriptedLLM(responses=["x"]))
    assert prov.name == "scripted"
