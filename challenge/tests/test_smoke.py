"""Smoke test: the composition over the sibling packages stays wired and runs
offline. Runnable directly (python tests/test_smoke.py) or via pytest.
"""
import json
from pathlib import Path

from challenge.agent import build_agent, build_store, guarded_input
from challenge.evaluation import build_judge, calibrate_judge, run_eval

DATA = Path(__file__).resolve().parent.parent / "data"


def test_agent_runs_offline():
    state = build_agent().run("what is 21 * 2")
    assert state.answer


def test_guardrail_redacts():
    out = guarded_input("email me at a@b.com")
    assert "a@b.com" not in out


def test_store_roundtrip():
    store = build_store()
    store.set("k", "v")
    assert store.get("k") == "v"


def test_eval_runs():
    summary = run_eval(str(DATA / "golden.jsonl"))
    assert summary.stats.n == 3


def test_calibration_runs():
    labels = {}
    for line in (DATA / "human_labels.jsonl").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        row = json.loads(line)
        labels[str(row["id"])] = float(row["human_score"])
    report = calibrate_judge(str(DATA / "golden.jsonl"), human_labels=labels)
    assert report.n == 3
    assert -1.0 <= report.cohen_kappa <= 1.0


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc!r}")
    print(f"\n{failures} failure(s)")
    raise SystemExit(1 if failures else 0)
