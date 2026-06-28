from inference_control_plane.db.session import get_session_factory
from inference_control_plane.worker.worker import persist_request_log

def _queue_request_log(
    background_tasks,
    *,
    tenant_id: str,
    user_id: str,
    api_key_hash: str,
    prompt: str,
    response: str,
    model_used: str,
    latency_ms: float,
    tokens: int,
    cost: float,
    cache_hit: bool,
    status_value: str,
    error_message: str | None,
) -> None:
    session_factory = get_session_factory()
    background_tasks.add_task(
        persist_request_log,
        session_factory,
        tenant_id=tenant_id,
        user_id=user_id,
        api_key_hash=api_key_hash,
        prompt=prompt,
        response=response,
        model_used=model_used,
        latency_ms=latency_ms,
        tokens=tokens,
        cost=cost,
        cache_hit=cache_hit,
        status_value=status_value,
        error_message=error_message,
    )
