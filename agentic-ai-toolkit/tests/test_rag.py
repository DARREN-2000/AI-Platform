import pytest

from agentic_toolkit.rag import (
    HashEmbedder,
    Retriever,
    TfidfEmbedder,
    build_grounded_prompt,
    chunk_text,
)


def test_chunking_short_text():
    assert chunk_text("hello world") == ["hello world"]
    assert chunk_text("") == []


def test_chunking_with_overlap():
    words = " ".join(str(i) for i in range(500))
    chunks = chunk_text(words, size=100, overlap=20)
    assert len(chunks) > 1
    assert all(chunks)


def test_retrieval_ranks_relevant_first():
    r = Retriever.from_texts(
        [
            "Paris is the capital of France.",
            "The mitochondria is the powerhouse of the cell.",
        ],
        chunk=False,
    )
    hits = r.retrieve("What is the capital of France?", k=2)
    assert "Paris" in hits[0][1].text
    assert hits[0][0] >= hits[1][0]


def test_tfidf_prefers_distinctive_match_over_common_words():
    r = Retriever.from_texts(
        [
            "Paris is the capital of France and sits on the Seine river.",
            "Berlin is the capital of Germany.",
            "The mitochondria is the powerhouse of the cell.",
        ],
        chunk=False,
    )
    hits = r.retrieve("capital of France", k=3)
    assert "Paris" in hits[0][1].text


def test_tfidf_requires_fit():
    with pytest.raises(RuntimeError):
        TfidfEmbedder().embed(["unfitted"])


def test_hash_embedder_needs_no_fit():
    r = Retriever.from_texts(
        ["Paris is the capital of France.", "Berlin is the capital of Germany."],
        embedder=HashEmbedder(),
        chunk=False,
    )
    assert len(r.retrieve("France", k=1)) == 1


def test_grounded_prompt_has_citations():
    r = Retriever.from_texts(["Paris is the capital of France."], chunk=False)
    hits = r.retrieve("capital of France", k=1)
    prompt = build_grounded_prompt("capital of France?", hits)
    assert "[1]" in prompt and "Paris" in prompt
