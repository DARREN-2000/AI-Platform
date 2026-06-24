"""Production reliability primitives agents and webhooks need: idempotency,
rate limiting, signature verification, and retries (re-exported from providers).
All dependency-free and deterministic via injectable clocks.
"""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from .providers import with_retries  # canonical retry helper


class IdempotencyStore:
    """Run a side-effecting function at most once per key. In-memory here; back
    it with Redis/Postgres in production. Critical for at-least-once delivery
    (webhooks, queues) where the same event can arrive twice."""

    def __init__(self) -> None:
        self._results: Dict[str, object] = {}

    def run_once(self, key: str, fn: Callable[[], object]) -> object:
        if key not in self._results:
            self._results[key] = fn()
        return self._results[key]

    def seen(self, key: str) -> bool:
        return key in self._results


@dataclass
class TokenBucket:
    """Token-bucket rate limiter. `now` is injectable so tests are deterministic."""

    capacity: float
    refill_per_sec: float
    now: Optional[Callable[[], float]] = None
    _tokens: float = field(default=None)
    _last: float = field(default=None)

    def __post_init__(self) -> None:
        import time as _time

        if self.now is None:
            self.now = _time.monotonic
        if self._tokens is None:
            self._tokens = self.capacity
        self._last = self.now()

    def allow(self, cost: float = 1.0) -> bool:
        t = self.now()
        self._tokens = min(self.capacity, self._tokens + (t - self._last) * self.refill_per_sec)
        self._last = t
        if self._tokens >= cost:
            self._tokens -= cost
            return True
        return False


def sign(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def verify_signature(secret: str, payload: bytes, signature: str) -> bool:
    """Constant-time HMAC-SHA256 verification (prevents timing attacks)."""
    return hmac.compare_digest(sign(secret, payload), signature)


__all__ = [
    "with_retries",
    "IdempotencyStore",
    "TokenBucket",
    "sign",
    "verify_signature",
]
