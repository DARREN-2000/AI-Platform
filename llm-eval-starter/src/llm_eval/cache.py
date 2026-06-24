"""Caching + cost/latency metering for judge providers.

LLM-as-judge burns API budget fast (samples x dataset x reruns). ``CachingProvider``
makes identical judge prompts free on repeat; ``MeteredProvider`` tracks estimated
tokens, latency, and USD so a run reports what it cost. Both implement the
``Provider`` Protocol, so they wrap any provider without touching eval logic.

Recommended live composition (only real calls are metered):
    meter = UsageMeter()
    judge = LLMJudge(provider=CachingProvider(MeteredProvider(OpenAIProvider(), meter)))
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .providers import Provider


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token) for cost accounting."""
    return max(1, (len(text or "") + 3) // 4)


# USD per 1K tokens as (input, output). Approximate; override on MeteredProvider.
PRICES: Dict[str, Tuple[float, float]] = {
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4o": (0.005, 0.015),
    "gpt-4.1-mini": (0.0004, 0.0016),
    "claude-3-5-sonnet": (0.003, 0.015),
    "claude-3-5-haiku": (0.0008, 0.004),
}


def price_for(model: str) -> Tuple[float, float]:
    for key, price in PRICES.items():
        if key in (model or ""):
            return price
    return (0.0, 0.0)


def _key(name: str, messages, temperature: float, max_tokens: int) -> str:
    payload = json.dumps(
        {
            "p": name,
            "m": [[m.role, m.content] for m in messages],
            "t": temperature,
            "k": max_tokens,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class UsageRecord:
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_ms: float

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class UsageMeter:
    records: List[UsageRecord] = field(default_factory=list)

    def add(self, record: UsageRecord) -> None:
        self.records.append(record)

    def summary(self) -> dict:
        calls = len(self.records)
        pt = sum(r.prompt_tokens for r in self.records)
        ct = sum(r.completion_tokens for r in self.records)
        cost = sum(r.cost_usd for r in self.records)
        latency = sum(r.latency_ms for r in self.records)
        return {
            "calls": calls,
            "prompt_tokens": pt,
            "completion_tokens": ct,
            "total_tokens": pt + ct,
            "cost_usd": round(cost, 6),
            "total_latency_ms": round(latency, 3),
            "avg_latency_ms": round(latency / calls, 3) if calls else 0.0,
        }


@dataclass
class MeteredProvider:
    """Times each call and records estimated tokens + cost into a UsageMeter."""

    inner: Provider
    meter: UsageMeter = field(default_factory=UsageMeter)
    price_per_1k_input: Optional[float] = None
    price_per_1k_output: Optional[float] = None

    @property
    def name(self) -> str:
        return getattr(self.inner, "name", "provider")

    def _prices(self) -> Tuple[float, float]:
        model = getattr(self.inner, "model", self.name)
        default_in, default_out = price_for(model)
        in_price = self.price_per_1k_input
        out_price = self.price_per_1k_output
        return (
            in_price if in_price is not None else default_in,
            out_price if out_price is not None else default_out,
        )

    def complete(self, messages, *, temperature: float = 0.0, max_tokens: int = 512) -> str:
        start = time.perf_counter()
        out = self.inner.complete(messages, temperature=temperature, max_tokens=max_tokens)
        latency_ms = (time.perf_counter() - start) * 1000.0
        prompt_tokens = sum(estimate_tokens(m.content) for m in messages)
        completion_tokens = estimate_tokens(out)
        in_price, out_price = self._prices()
        cost = (prompt_tokens / 1000.0) * in_price + (completion_tokens / 1000.0) * out_price
        self.meter.add(
            UsageRecord(
                provider=self.name,
                model=str(getattr(self.inner, "model", self.name)),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
            )
        )
        return out


@dataclass
class CachingProvider:
    """In-memory cache keyed by (provider, messages, temperature, max_tokens)."""

    inner: Provider
    cache: Dict[str, str] = field(default_factory=dict)
    hits: int = 0
    misses: int = 0

    @property
    def name(self) -> str:
        return getattr(self.inner, "name", "provider")

    def complete(self, messages, *, temperature: float = 0.0, max_tokens: int = 512) -> str:
        key = _key(self.name, messages, temperature, max_tokens)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        out = self.inner.complete(messages, temperature=temperature, max_tokens=max_tokens)
        self.cache[key] = out
        return out

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 4) if total else 0.0,
            "size": len(self.cache),
        }
