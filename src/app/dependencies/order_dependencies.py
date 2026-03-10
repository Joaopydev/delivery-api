from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_database
from app.events.dispatcher import EventDispatcher

from app.services.orders.OrderService import OrderService

from app.repository.order_repository import OrderRepository
from app.repository.account_repository import AccountRepository

from app.dependencies.dispatcher_dependencies import get_event_dispatcher
from app.dependencies.account_dependencies import get_account_repository


def get_order_repository(session: AsyncSession = Depends(get_database)) -> OrderRepository:
    return OrderRepository(session=session)

def get_order_service(
    order_repository: OrderRepository = Depends(get_order_repository),
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher),
    account_repository: AccountRepository = Depends(get_account_repository)
) -> OrderService:

    return OrderService(
        account_repository=account_repository,
        order_repository=order_repository,
        event_dispatcher=event_dispatcher,
    )
