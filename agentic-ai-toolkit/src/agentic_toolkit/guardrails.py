"""Lightweight, deterministic guardrails: PII redaction, prompt-injection
heuristics, length limits, and blocklists, composed into a small pipeline.

These are defense-in-depth *heuristics* (the same shape you would back with a
moderation API or a classifier model in production), not a security guarantee.
They make the safety story concrete, testable, and offline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

Check = Callable[[str], Tuple[str, List[str]]]

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
CREDIT_CARD_RE = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE_RE = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")

# Ordered so multi-field patterns mask before narrower ones.
PII_PATTERNS: List[Tuple[str, "re.Pattern[str]"]] = [
    ("email", EMAIL_RE),
    ("credit_card", CREDIT_CARD_RE),
    ("ssn", SSN_RE),
    ("phone", PHONE_RE),
]

INJECTION_PATTERNS = [
    "ignore previous",
    "ignore all previous",
    "ignore the above",
    "disregard the above",
    "disregard previous",
    "forget your instructions",
    "forget all previous",
    "reveal your system prompt",
    "print your system prompt",
    "show your system prompt",
    "you are now",
    "developer mode",
    "do anything now",
    "override your instructions",
]


def find_pii(text: str) -> Dict[str, List[str]]:
    """Return a mapping of pii-type -> matched substrings."""
    out: Dict[str, List[str]] = {}
    for label, pat in PII_PATTERNS:
        matches = pat.findall(text)
        if matches:
            out[label] = [m if isinstance(m, str) else m[0] for m in matches]
    return out


def redact_pii(text: str, mask: str = "[REDACTED]") -> str:
    for _label, pat in PII_PATTERNS:
        text = pat.sub(mask, text)
    return text


def detect_prompt_injection(text: str) -> List[str]:
    low = text.lower()
    return [p for p in INJECTION_PATTERNS if p in low]


# --- composable checks: each maps text -> (possibly-edited text, violations) --
def pii_redactor(mask: str = "[REDACTED]") -> Check:
    def check(text: str) -> Tuple[str, List[str]]:
        found = find_pii(text)
        if not found:
            return text, []
        return redact_pii(text, mask), [f"pii:{k}" for k in found]

    return check


def injection_detector() -> Check:
    def check(text: str) -> Tuple[str, List[str]]:
        return text, [f"injection:{h}" for h in detect_prompt_injection(text)]

    return check


def max_length(limit: int) -> Check:
    def check(text: str) -> Tuple[str, List[str]]:
        if len(text) <= limit:
            return text, []
        return text[:limit], [f"truncated:{len(text)}->{limit}"]

    return check


def blocklist(words: List[str]) -> Check:
    lowered = [w.lower() for w in words]

    def check(text: str) -> Tuple[str, List[str]]:
        low = text.lower()
        return text, [f"blocked:{w}" for w in lowered if w in low]

    return check


class GuardrailViolation(Exception):
    """Raised by Guardrail.enforce when a violation is found."""


@dataclass
class GuardResult:
    ok: bool
    text: str
    violations: List[str] = field(default_factory=list)


@dataclass
class Guardrail:
    """Runs an ordered list of checks; later checks see earlier edits."""

    checks: List[Check] = field(default_factory=list)

    def add(self, check: Check) -> "Guardrail":
        self.checks.append(check)
        return self

    def run(self, text: str) -> GuardResult:
        violations: List[str] = []
        for check in self.checks:
            text, found = check(text)
            violations.extend(found)
        return GuardResult(ok=not violations, text=text, violations=violations)

    def enforce(self, text: str) -> str:
        result = self.run(text)
        if not result.ok:
            raise GuardrailViolation(", ".join(result.violations))
        return result.text


def default_input_guard(max_chars: int = 8000) -> Guardrail:
    return Guardrail(
        checks=[injection_detector(), pii_redactor(), max_length(max_chars)]
    )


def default_output_guard() -> Guardrail:
    return Guardrail(checks=[pii_redactor()])
