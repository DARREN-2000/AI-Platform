"""Minimal helpers to load the frozen traces and the seed labels.

This is the only data plumbing we give you — the eval data model, evaluators,
scoring, calibration, and reporting are yours to design. ``load_traces`` returns each
trace as-is.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_traces(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Return the list of recorded agent runs."""
    path = Path(path) if path else DATA_DIR / "traces.json"
    return json.loads(path.read_text())


def load_seed_labels(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Return the small hand-labelled sample, keyed by trace_id."""
    path = Path(path) if path else DATA_DIR / "seed_labels.json"
    return json.loads(path.read_text())
