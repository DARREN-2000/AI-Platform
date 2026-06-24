from agentic_toolkit.providers import RuleBasedLLM
from agentic_toolkit.rag import Retriever
from agentic_toolkit.service import ChatService


def test_chat_with_retrieval_and_trace():
    svc = ChatService(
        provider=RuleBasedLLM(),
        retriever=Retriever.from_texts(
            [
                "Paris is the capital of France.",
                "Berlin is the capital of Germany.",
            ],
            chunk=False,
        ),
    )
    out = svc.chat("What is the capital of France?", k=1)
    assert out["retrieved"]
    assert "Paris" in out["retrieved"][0]["text"]
    assert out["answer"]
    assert out["trace"]["name"] == "chat"


def test_chat_without_retriever_still_answers():
    svc = ChatService(provider=RuleBasedLLM())
    out = svc.chat("what is 8 * 8?")
    assert "64" in (out["answer"] or "")
    assert out["trajectory"][0]["tool"] == "calculator"
    assert out["retrieved"] == []
