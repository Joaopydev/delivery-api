from fastapi import Depends

from app.db.connection import get_database
from app.db.models.schemas import Order
from app.schemas.order_schemas import CurrentOrder
from app.core.exceptions import OrderNotFoundError

async def order_exists(
    current_order: CurrentOrder,
    session = Depends(get_database)
) -> Order:

    order = await session.get(Order, current_order.order_id)
    if not order:
        raise OrderNotFoundError()
    return order
