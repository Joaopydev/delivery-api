from fastapi import Depends, HTTPException, status

from ..db.connection import get_database
from ..db.models.schemas import Order
from ..schemas.order_schemas import CurrentOrder

async def order_exists(
    current_order: CurrentOrder,
    session = Depends(get_database)
) -> Order:
    
    order = await session.get(Order, current_order.order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order not found"
        )
    
    return order
