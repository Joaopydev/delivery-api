import asyncio
from typing import Dict, Any

from celery import shared_task
from openai import RateLimitError, APIConnectionError, InternalServerError

from app.ai.services.ReadyTimeEstimationService import ReadyTimeEstimationService

from app.db.connection import get_session_to_worker
from app.db.models.schemas import Order

@shared_task(
    bind=True,
    autoretry_for=(RateLimitError, APIConnectionError, InternalServerError),
    retry_backoff=True,
    max_retries=5
)
def estimate_order_time(self, data: Dict[str, Any]):
    async def run_task():
        async with get_session_to_worker() as session:
            target_order = data["target_order"]
            ai_estamation_service = ReadyTimeEstimationService(session=session)
            estimated_time = await ai_estamation_service.estimate(target_order=target_order)
            order: Order = await session.get(Order, int(target_order["id"]))
            order.estimated_time = estimated_time

            await session.commit()
            await session.refresh(order)
        
    asyncio.run(run_task())

