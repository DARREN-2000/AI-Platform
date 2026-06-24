"""A tiny, dependency-free RAG pipeline: chunk -> embed -> store -> retrieve ->
ground.

Two embedders ship, both behind the same `Embedder` Protocol:
- `TfidfEmbedder` (default): corpus-fitted TF-IDF. IDF down-weights ubiquitous
  words (the, of, is) and up-weights distinctive ones (france, mitochondria),
  which is the right default for lexical retrieval.
- `HashEmbedder`: stateless bag-of-words hashing. No corpus fit required; handy
  for streaming/online indexing where you cannot pre-fit a vocabulary.

Swap in a real embedding model by implementing `Embedder` and backing
`VectorStore` with pgvector/FAISS/Qdrant.
"""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Protocol, Sequence, Tuple

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    return _TOKEN.findall(text.lower())


def chunk_text(text: str, *, size: int = 200, overlap: int = 40) -> List[str]:
    """Word-window chunking with overlap. Overlap preserves context across
    boundaries so a fact split between two chunks is still retrievable."""
    if size <= 0:
        raise ValueError("size must be > 0")
    words = text.split()
    if not words:
        return []
    step = max(1, size - overlap)
    chunks: List[str] = []
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + size])
        if chunk:
            chunks.append(chunk)
        if i + size >= len(words):
            break
    return chunks


class Embedder(Protocol):
    dim: int

    def embed(self, texts: Sequence[str]) -> List[List[float]]: ...


@dataclass
class TfidfEmbedder:
    """Corpus-fitted TF-IDF embedder. Call `fit(corpus)` before embedding.

    Uses smoothed IDF = ln((1 + N) / (1 + df)) + 1 and L2-normalizes vectors so
    cosine similarity is just a dot product. Tokens unseen at fit time are
    ignored at query time.
    """

    vocab: Dict[str, int] = field(default_factory=dict)
    idf: List[float] = field(default_factory=list)
    fitted: bool = False

    @property
    def dim(self) -> int:
        return len(self.vocab)

    def fit(self, corpus: Sequence[str]) -> "TfidfEmbedder":
        df: Counter = Counter()
        for text in corpus:
            for tok in set(tokenize(text)):
                df[tok] += 1
        self.vocab = {tok: i for i, tok in enumerate(sorted(df))}
        n = len(list(corpus))
        self.idf = [0.0] * len(self.vocab)
        for tok, i in self.vocab.items():
            self.idf[i] = math.log((1 + n) / (1 + df[tok])) + 1.0
        self.fitted = True
        return self

    def _embed_one(self, text: str) -> List[float]:
        v = [0.0] * len(self.vocab)
        for tok, count in Counter(tokenize(text)).items():
            i = self.vocab.get(tok)
            if i is not None:
                v[i] = count * self.idf[i]
        norm = math.sqrt(sum(x * x for x in v))
        return [x / norm for x in v] if norm else v

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        if not self.fitted:
            raise RuntimeError("TfidfEmbedder must be fit() on the corpus first")
        return [self._embed_one(t) for t in texts]


@dataclass
class HashEmbedder:
    """Stateless bag-of-words hashing embedder (md5 for stable hashing across
    processes). No corpus fit needed; good for online/streaming indexing."""

    dim: int = 256

    def _embed_one(self, text: str) -> List[float]:
        v = [0.0] * self.dim
        for tok in tokenize(text):
            idx = int(hashlib.md5(tok.encode()).hexdigest(), 16) % self.dim
            v[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in v))
        return [x / norm for x in v] if norm else v

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        return [self._embed_one(t) for t in texts]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Dot product; inputs are expected to be unit-normalized vectors."""
    return sum(x * y for x, y in zip(a, b))


@dataclass
class Document:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass
class VectorStore:
    embedder: Embedder
    _docs: List[Document] = field(default_factory=list)
    _vecs: List[List[float]] = field(default_factory=list)

    def add(self, docs: Sequence[Document]) -> None:
        vecs = self.embedder.embed([d.text for d in docs])
        self._docs.extend(docs)
        self._vecs.extend(vecs)

    def search(self, query: str, k: int = 3) -> List[Tuple[float, Document]]:
        if not self._docs:
            return []
        q = self.embedder.embed([query])[0]
        scored = [(cosine(q, v), d) for v, d in zip(self._vecs, self._docs)]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:k]


@dataclass
class Retriever:
    store: VectorStore

    @classmethod
    def from_texts(
        cls,
        texts: Sequence[str],
        *,
        embedder: Embedder = None,
        chunk: bool = True,
    ) -> "Retriever":
        docs: List[Document] = []
        doc_texts: List[str] = []
        for i, t in enumerate(texts):
            pieces = chunk_text(t) if chunk else [t]
            for j, p in enumerate(pieces):
                docs.append(Document(id=f"doc{i}.{j}", text=p))
                doc_texts.append(p)
        if embedder is None:
            embedder = TfidfEmbedder().fit(doc_texts)
        elif isinstance(embedder, TfidfEmbedder) and not embedder.fitted:
            embedder.fit(doc_texts)
        store = VectorStore(embedder=embedder)
        store.add(docs)
        return cls(store=store)

    def retrieve(self, query: str, k: int = 3) -> List[Tuple[float, Document]]:
        return self.store.search(query, k)


def build_grounded_prompt(question: str, hits: List[Tuple[float, Document]]) -> str:
    ctx = "\n".join(f"[{i + 1}] {d.text}" for i, (_, d) in enumerate(hits))
    return (
        "Answer using ONLY the context below. Cite sources inline like [1].\n\n"
        f"Context:\n{ctx}\n\nQuestion: {question}\nAnswer:"
    )
