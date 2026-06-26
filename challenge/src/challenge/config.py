"""Env-driven settings for the challenge workspace."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    provider: str = "rules"          # agent provider (rules=offline)
    model: Optional[str] = None
    max_steps: int = 6
    eval_provider: str = "mock"      # judge provider (mock=offline)
    dataset_path: str = "data/golden.jsonl"
    database_url: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            provider=os.getenv("CHALLENGE_PROVIDER", "rules"),
            model=os.getenv("CHALLENGE_MODEL") or None,
            max_steps=int(os.getenv("CHALLENGE_MAX_STEPS", "6")),
            eval_provider=os.getenv("CHALLENGE_EVAL_PROVIDER", "mock"),
            dataset_path=os.getenv("CHALLENGE_DATASET", "data/golden.jsonl"),
            database_url=os.getenv("DATABASE_URL") or None,
        )
