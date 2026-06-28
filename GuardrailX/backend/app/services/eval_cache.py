from typing import Any, Dict

class EvaluationCache:
    """In-memory cache for fast-path evaluation of prompts."""
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, cache_key: str) -> Dict[str, Any]:
        return self._cache.get(cache_key)

    def set(self, cache_key: str, result: Dict[str, Any]) -> None:
        self._cache[cache_key] = result

    def clear(self) -> None:
        self._cache.clear()
