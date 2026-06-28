import logging
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from inference_control_plane.models.request_log import RequestLog

logger = logging.getLogger(__name__)

async def persist_request_log(
    session_factory: async_sessionmaker[AsyncSession],
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
    async with session_factory() as session:
        try:
            session.add(
                RequestLog(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    api_key_hash=api_key_hash,
                    prompt=prompt,
                    response=response,
                    model_used=model_used,
                    latency_ms=max(latency_ms, 0.0),
                    tokens=max(tokens, 0),
                    cost=Decimal(str(max(cost, 0.0))),
                    cache_hit=cache_hit,
                    status=status_value,
                    error_message=error_message,
                )
            )
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("Failed to persist request log.")
