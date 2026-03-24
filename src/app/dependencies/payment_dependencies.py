from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.payments.payment import PaymentService
from app.services.payments.webhook import WebHookService
from app.repository.payment_repository import PaymentRepository

from app.db.connection import get_database
from app.dependencies.dispatcher_dependencies import get_event_dispatcher
from app.events.dispatcher import EventDispatcher


def get_payment_repository(session: AsyncSession = Depends(get_database)) -> PaymentRepository:
    return PaymentRepository(session=session)

def get_webhook_service(
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher),
    payment_repository: PaymentRepository = Depends(get_payment_repository),
) -> WebHookService:

    return WebHookService(
        event_dispatcher=event_dispatcher,
        payment_repository=payment_repository,
    )

def get_payment_service(
    payment_repository: PaymentRepository = Depends(get_payment_repository)
) -> PaymentService:

    return PaymentService(payment_repository=payment_repository)
