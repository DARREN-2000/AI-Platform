"""Tests for the retry/backoff decorator."""
import httpx
import pytest

from tools.resilience import with_retry


async def test_retries_then_succeeds(monkeypatch):
    calls = {"n": 0}

    async def _no_sleep(_):
        return None

    monkeypatch.setattr("tools.resilience.asyncio.sleep", _no_sleep)

    @with_retry(max_attempts=3, base_delay=0)
    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            resp = httpx.Response(503, request=httpx.Request("GET", "https://x"))
            raise httpx.HTTPStatusError("boom", request=resp.request, response=resp)
        return "ok"

    assert await flaky() == "ok"
    assert calls["n"] == 3


async def test_non_retryable_raises_immediately(monkeypatch):
    calls = {"n": 0}

    @with_retry(max_attempts=3, base_delay=0)
    async def forbidden():
        calls["n"] += 1
        resp = httpx.Response(403, request=httpx.Request("GET", "https://x"))
        raise httpx.HTTPStatusError("no", request=resp.request, response=resp)

    with pytest.raises(httpx.HTTPStatusError):
        await forbidden()
    assert calls["n"] == 1
