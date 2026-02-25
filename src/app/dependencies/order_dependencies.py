from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_database
from app.repository.order_repository import OrderRepository
from app.services.orders.OrderService import OrderService


def get_order_repository(session: AsyncSession = Depends(get_database)) -> OrderRepository:
    return OrderRepository(session=session)

def get_order_service(order_repository: OrderRepository = Depends(get_order_repository)) -> OrderService:
    return OrderService(order_repository=order_repository)