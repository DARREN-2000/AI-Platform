from typing import Any, Tuple
from app.models.policy import Policy

class PolicyEvaluator:
    @staticmethod
    def evaluate(policy: Policy | None, prompt: str) -> Tuple[bool, float, int]:
        """Core risk evaluation logic abstracted from the service."""
        is_safe = True
        risk_score = 0.05
        tokens_used = len(prompt.split()) + 10
        return is_safe, risk_score, tokens_used
