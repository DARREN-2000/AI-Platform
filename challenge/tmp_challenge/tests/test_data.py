"""Sanity checks for the provided data — these pass out of the box.

Run them first to confirm your environment is set up:  pytest -q
Add your own tests as you build.
"""

from __future__ import annotations

from synera_eval.loader import load_seed_labels, load_traces


def test_traces_load() -> None:
    traces = load_traces()
    assert len(traces) >= 50
    assert all("trace_id" in t and "query" in t for t in traces)


def test_trace_ids_unique() -> None:
    ids = [t["trace_id"] for t in load_traces()]
    assert len(ids) == len(set(ids))


def test_seed_labels_reference_real_traces() -> None:
    trace_ids = {t["trace_id"] for t in load_traces()}
    seed = load_seed_labels()
    assert 0 < len(seed) < len(trace_ids)  # only a small sample is labelled
    assert all(trace_id in trace_ids for trace_id in seed)
