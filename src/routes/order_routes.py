from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from ..schemas.order_schemas import OrderSchema

from ..db.connection import get_database
from ..services.orders.OrderService import OrderService

order_router = APIRouter(prefix="/orders", tags=["orders"])


@order_router.get("/")
async def orders() -> dict:
    return {
        "Orders": "pedidos"
    }


@order_router.post("/create-order")
async def create_order(order_data: OrderSchema, session: AsyncSession = Depends(get_database)) -> Dict[str, Any]:
    order_service = OrderService()
    new_order = order_service.create_order(order_data=order_data)

    return {"content": f"Order created successfully. OrderId: {new_order.id}"}