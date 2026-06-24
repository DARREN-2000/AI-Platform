from llm_eval.cache import CachingProvider, MeteredProvider, UsageMeter
from llm_eval.providers import Message


class CountingProvider:
    name = "counting"
    model = "gpt-4o-mini"

    def __init__(self):
        self.calls = 0

    def complete(self, messages, *, temperature=0.0, max_tokens=512):
        self.calls += 1
        return '{"score": 5, "reasoning": "ok"}'


def test_cache_avoids_second_call():
    inner = CountingProvider()
    cached = CachingProvider(inner)
    m = [Message("user", "judge this")]
    cached.complete(m)
    cached.complete(m)
    assert inner.calls == 1
    assert cached.stats()["hits"] == 1


def test_meter_records_usage():
    meter = UsageMeter()
    metered = MeteredProvider(CountingProvider(), meter)
    metered.complete([Message("user", "x")])
    summary = meter.summary()
    assert summary["calls"] == 1
    assert summary["total_tokens"] > 0


def test_cache_over_meter_only_meters_misses():
    meter = UsageMeter()
    provider = CachingProvider(MeteredProvider(CountingProvider(), meter))
    m = [Message("user", "x")]
    provider.complete(m)
    provider.complete(m)
    assert meter.summary()["calls"] == 1
