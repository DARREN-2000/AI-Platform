from __future__ import annotations
from app.models.policy_evaluator import PolicyEvaluator

import asyncio
import time
import uuid
from typing import Any

import mlflow

from app.models.policy import Policy
from app.repositories.policies import PolicyRepository
from app.services.base import CRUDService


class PolicyService(CRUDService[Policy]):
    repository: PolicyRepository

    def __init__(self, repository: PolicyRepository) -> None:
        super().__init__(repository)

    async def get_by_name(self, tenant_id, name: str) -> Policy | None:
        return await self.repository.get_by_name(tenant_id, name)

    async def evaluate_policy(self, tenant_id: uuid.UUID, name: str, prompt: str) -> dict[str, Any]:
        """Evaluate a prompt against a policy, simulating latency and token usage.
        Logs metrics and evaluation details to MLflow.
        """
        start_time = time.time()
        policy = await self.get_by_name(tenant_id, name)

        is_safe, risk_score, tokens_used = PolicyEvaluator.evaluate(policy, prompt)

        latency = time.time() - start_time

        def _log_to_mlflow():
            try:
                nested = mlflow.active_run() is not None
                with mlflow.start_run(run_name=f"evaluate_policy_{name}", nested=nested):
                    mlflow.log_param("tenant_id", str(tenant_id))
                    mlflow.log_param("policy_name", name)
                    if policy:
                        mlflow.log_param("policy_id", str(policy.id))
                    mlflow.log_metric("latency_seconds", latency)
                    mlflow.log_metric("tokens_used", tokens_used)
                    mlflow.log_metric("risk_score", risk_score)
                    mlflow.log_param("is_safe", str(is_safe))
            except Exception as e:
                from app.core.logging import get_logger
                logger = get_logger(__name__)
                logger.error(f"Failed to log metrics to MLflow: {e}")

        asyncio.create_task(asyncio.to_thread(_log_to_mlflow))

        return {
            "is_safe": is_safe,
            "risk_score": risk_score,
            "tokens_used": tokens_used,
            "latency": latency,
            "policy": policy.name if policy else None,
        }
