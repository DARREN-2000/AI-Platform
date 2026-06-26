"""Reference-based metrics: deterministic scoring when you have gold answers.

Not every eval needs an LLM judge. When references exist, cheap exact-match,
token-F1, and cosine-over-hashed-bag-of-words metrics are fast, free, and fully
reproducible. Use them alongside or instead of the LLM judge.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Dict, List

_WORD_RE = re.compile(r"[a-z0-9]+")


def normalize(text: str) -> str:
    return " ".join(_WORD_RE.findall(text.lower()))


def tokenize(text: str) -> List[str]:
    return _WORD_RE.findall(text.lower())


def exact_match(prediction: str, reference: str) -> float:
    return 1.0 if normalize(prediction) == normalize(reference) else 0.0


def token_f1(prediction: str, reference: str) -> float:
    pred = tokenize(prediction)
    ref = tokenize(reference)
    if not pred and not ref:
        return 1.0
    if not pred or not ref:
        return 0.0
    ref_counts: Dict[str, int] = {}
    for t in ref:
        ref_counts[t] = ref_counts.get(t, 0) + 1
    seen: Dict[str, int] = {}
    overlap = 0
    for t in pred:
        seen[t] = seen.get(t, 0) + 1
        if seen[t] <= ref_counts.get(t, 0):
            overlap += 1
    if overlap == 0:
        return 0.0
    precision = overlap / len(pred)
    recall = overlap / len(ref)
    return 2 * precision * recall / (precision + recall)


def _vector(tokens: List[str], dim: int = 256) -> List[float]:
    vec = [0.0] * dim
    for t in tokens:
        bucket = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16) % dim
        vec[bucket] += 1.0
    return vec


def cosine_similarity(a: str, b: str, dim: int = 256) -> float:
    va = _vector(tokenize(a), dim)
    vb = _vector(tokenize(b), dim)
    dot = sum(x * y for x, y in zip(va, vb))
    na = math.sqrt(sum(x * x for x in va))
    nb = math.sqrt(sum(y * y for y in vb))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def keyword_recall(prediction: str, keywords: List[str]) -> float:
    if not keywords:
        return 1.0
    low = prediction.lower()
    hits = sum(1 for k in keywords if k.lower() in low)
    return hits / len(keywords)
