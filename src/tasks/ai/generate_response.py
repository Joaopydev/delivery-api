import asyncio
from typing import Dict, Any

from celery import shared_task
from openai import RateLimitError, APIConnectionError, InternalServerError

from app.ai.services.estimated_time_service import ReadyTimeEstimationService
from app.services.orders.order import OrderService
from app.repository.order_repository import OrderRepository
from app.repository.account_repository import AccountRepository
from app.events.dispatcher_instance import dispatcher

from app.db.connection import get_session_to_worker

@shared_task(
    bind=True,
    autoretry_for=(RateLimitError, APIConnectionError, InternalServerError, ValueError),
    retry_backoff=True,
    max_retries=5
)
def estimate_order_time(_, data: Dict[str, Any]):
    async def run_task():
        async with get_session_to_worker() as session:
            order_repository = OrderRepository(session=session)
            ai_estamation_service = ReadyTimeEstimationService(
                order_repository=order_repository,
                order_service=OrderService(
                    account_repository=AccountRepository(session),
                    order_repository=order_repository,
                    event_dispatcher=dispatcher,
                )
            )
            await ai_estamation_service.estimate(data["target_order"])
    asyncio.run(run_task())
