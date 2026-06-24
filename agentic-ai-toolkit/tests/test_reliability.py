from agentic_toolkit.reliability import (
    IdempotencyStore,
    TokenBucket,
    sign,
    verify_signature,
    with_retries,
)


def test_idempotency_runs_once():
    store = IdempotencyStore()
    calls = []

    def fn():
        calls.append(1)
        return "result"

    assert store.run_once("k", fn) == "result"
    assert store.run_once("k", fn) == "result"
    assert len(calls) == 1
    assert store.seen("k")


def test_token_bucket_limits_and_refills():
    clock = {"t": 0.0}
    tb = TokenBucket(capacity=2, refill_per_sec=1.0, now=lambda: clock["t"])
    assert tb.allow()
    assert tb.allow()
    assert not tb.allow()
    clock["t"] = 1.0
    assert tb.allow()
    assert not tb.allow()


def test_signature_roundtrip_and_rejection():
    sig = sign("secret", b"payload")
    assert verify_signature("secret", b"payload", sig)
    assert not verify_signature("secret", b"payload", "deadbeef")
    assert not verify_signature("wrong-secret", b"payload", sig)


def test_with_retries_eventually_succeeds():
    state = {"n": 0}

    def flaky():
        state["n"] += 1
        if state["n"] < 3:
            raise ValueError("transient")
        return "ok"

    assert with_retries(flaky, attempts=5, base_delay=0.0) == "ok"
    assert state["n"] == 3
