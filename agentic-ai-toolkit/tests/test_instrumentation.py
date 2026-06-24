from agentic_toolkit.instrumentation import CachingProvider, MeteredProvider, UsageMeter
from agentic_toolkit.providers import Message


class CountingProvider:
    name = "counting"
    model = "gpt-4o-mini"

    def __init__(self):
        self.calls = 0

    def complete(self, messages, *, temperature=0.0, max_tokens=512):
        self.calls += 1
        return "FINAL: ok"


def _msgs():
    return [Message("user", "hello world")]


def test_cache_avoids_second_call():
    inner = CountingProvider()
    cached = CachingProvider(inner)
    a = cached.complete(_msgs())
    b = cached.complete(_msgs())
    assert a == b == "FINAL: ok"
    assert inner.calls == 1
    stats = cached.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_cache_distinguishes_prompts():
    inner = CountingProvider()
    cached = CachingProvider(inner)
    cached.complete([Message("user", "a")])
    cached.complete([Message("user", "b")])
    assert inner.calls == 2


def test_meter_records_cost_and_latency():
    meter = UsageMeter()
    metered = MeteredProvider(CountingProvider(), meter)
    metered.complete(_msgs())
    summary = meter.summary()
    assert summary["calls"] == 1
    assert summary["total_tokens"] > 0
    assert summary["cost_usd"] >= 0.0
    assert summary["total_latency_ms"] >= 0.0


def test_cache_over_meter_only_meters_real_calls():
    meter = UsageMeter()
    provider = CachingProvider(MeteredProvider(CountingProvider(), meter))
    provider.complete(_msgs())
    provider.complete(_msgs())  # cache hit: must not reach the meter
    assert meter.summary()["calls"] == 1
    assert provider.stats()["hits"] == 1
