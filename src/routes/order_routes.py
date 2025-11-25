from typing import Dict, Any, Optional, List, Annotated
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, status, Query

from ..schemas.order_schemas import OrderSchema, CreateOrderSchema

from ..db.connection import get_database
from ..services.orders.OrderService import OrderService
from ..lib.token_jwt import verify_token

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verify_token)])


@order_router.post("/create-order", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: CreateOrderSchema,
    session: AsyncSession = Depends(get_database),
) -> Dict[str, Any]:
    
    order_service = OrderService(session=session)
    new_order = await order_service.create_order(order_data=order_data)

    return {"content": f"Order created successfully. OrderId: {new_order.id}"}


@order_router.post("/cancel-order/{order_id}", status_code=status.HTTP_200_OK)
async def cancel_order(
    order_id: int,
    request: Request,
    session: AsyncSession = Depends(get_database)
):
    order_service = OrderService(session=session)
    order = await order_service.cancel_order(order_id=order_id, user_id=int(request.state.user_id))
    return {
        "content": f"Order canceled successfully. OrderId: {order_id}",
        "order": order
    }


@order_router.post("/list-orders")
async def list_orders(
    request: Request,
    session: AsyncSession = Depends(get_database),
    start_date: Annotated[Optional[date], Query(description="Parameter to list orders according to a start date.")] = None,
    end_date: Annotated[Optional[date], Query(description="Parameter to list orders according to an end date.")] = None,
) -> Dict[str, List[OrderSchema]]:
    
    order_service = OrderService(session=session)
    orders = await order_service.list_orders(
        user_id=request.state.user_id,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "orders": orders
    }