"""Resilience helpers: retry with exponential backoff + jitter for flaky HTTP calls."""
import asyncio
import logging
import random
from functools import wraps
from typing import Any, Callable, TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")

RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def with_retry(
    max_attempts: int = 4,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
) -> Callable:
    """Decorator for async functions that retries on transient HTTP errors.

    Honors GitHub/Notion `Retry-After` headers when a 429 is returned.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while True:
                attempt += 1
                try:
                    return await func(*args, **kwargs)
                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code
                    if status not in RETRYABLE_STATUS or attempt >= max_attempts:
                        raise
                    retry_after = exc.response.headers.get("Retry-After")
                    delay = (
                        float(retry_after)
                        if retry_after and retry_after.isdigit()
                        else min(max_delay, base_delay * 2 ** (attempt - 1))
                    )
                    delay += random.uniform(0, 0.3)  # jitter
                    logger.warning(
                        "retrying after %.2fs (attempt %d/%d, status %d)",
                        delay, attempt, max_attempts, status,
                    )
                    await asyncio.sleep(delay)
                except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                    if attempt >= max_attempts:
                        raise
                    delay = min(max_delay, base_delay * 2 ** (attempt - 1)) + random.uniform(0, 0.3)
                    logger.warning("network error, retrying after %.2fs: %s", delay, exc)
                    await asyncio.sleep(delay)

        return wrapper

    return decorator
