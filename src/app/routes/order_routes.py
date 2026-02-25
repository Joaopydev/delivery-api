from typing import ( 
    Dict,
    Any,
    List, 
)
from fastapi import (
    APIRouter,
    Depends,
    Request, 
    status,
)

from app.dependencies.order_dependencies import get_order_service
from app.db.models.schemas import OrderStatus
from app.services.orders.OrderService import OrderService
from app.lib.token_jwt import (
    verify_token,
    require_admin
)
from app.schemas.order_schemas import (
    OrderSchema,
    CreateOrderSchema,
    OrderItemSchema, 
    DeleteItemFromOrderSchema,
)
from tasks.emails.send_email import (
    send_confirmation_email,
    send_order_ready_email,
)
from tasks.ai.generate_response import estimate_order_time

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verify_token)])


@order_router.post("/create-order", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: CreateOrderSchema,
    order_service: OrderService = Depends(get_order_service),
) -> Dict[str, Any]:
    
    new_order = await order_service.create_order(order_data=order_data)
    return {"content": f"Order created successfully. OrderId: {new_order.id}"}


@order_router.post("/cancel-order/{order_id}", status_code=status.HTTP_200_OK)
async def cancel_order(
    order_id: int,
    request: Request,
    order_service: OrderService = Depends(get_order_service),
):

    order = await order_service.cancel_order(order_id=order_id, user_id=int(request.state.user["id"]))
    return {
        "content": f"Order canceled successfully. OrderId: {order_id}",
        "order": order
    }


@order_router.post("/list-orders")
async def list_orders(
    status: OrderStatus,
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(require_admin)
) -> Dict[str, List[OrderSchema]]:
    
    orders = await order_service.list_orders(
        user_id=int(request.state.user["id"]),
        order_status=status
    )

    return {"orders": orders}


@order_router.post("/add-item/{order_id}", status_code=status.HTTP_201_CREATED)
async def add_item_to_order(
    order_id: int,
    order_item_data: OrderItemSchema,
    request: Request,
    order_service: OrderService = Depends(get_order_service),
) -> Dict[str, int]:
    
    order_item = await order_service.add_item_to_order(
        order_id=order_id,
        user_id=int(request.state.user["id"]),
        order_item_data=order_item_data,
    )
    return {"order_item": order_item.id}


@order_router.delete("/delete-order-item/{order_item_id}", status_code=status.HTTP_200_OK)
async def delete_item_from_order(
    order_item_id: int,
    order: DeleteItemFromOrderSchema,
    request: Request,
    order_service: OrderService = Depends(get_order_service),
) -> Dict[str, str]:

    await order_service.delete_item_from_order(
        order_id=order.id,
        order_item_id=order_item_id,
        user_id=int(request.state.user["id"]),
    )

    return {"message": f"Order item {order_item_id} succesfully deleted."}


@order_router.post("/confirm-order/{order_id}", status_code=status.HTTP_200_OK)
async def confirm_order(
    order_id: int,
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(require_admin),
) -> Dict[str, OrderSchema]:
    
    """Only the admin can call this route"""

    order = await order_service.confirm_order(
        order_id=order_id,
        user_id=int(request.state.user["id"])
    )

    send_confirmation_email.delay({
        "to": request.state.user["email"],
        "name": request.state.user["name"],
        "order_id": str(order.id)
    })
    estimate_order_time.delay({
        "target_order": order.to_dict
    })
    
    return {"order": order}

@order_router.post("/send-order/{order_id}")
async def send_order(
    order_id: int,
    request: Request,
    order_service: OrderService = Depends(get_order_service),
) -> Dict[str, OrderSchema]:
    
    order = await order_service.send_order(
        order_id=order_id,
        user_id=int(request.state.user["id"])
    )

    return {"order": order}

@order_router.post("/confirm-order-readiness/{order_id}")
async def confirm_order_readiness(
    order_id: int,
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(require_admin)
) -> Dict[str, OrderSchema]:
    
    """Only the admin can call this route"""
    
    order = await order_service.confirm_order_readiness(
        order_id=order_id,
        user_id=int(request.state.user["id"]),
    )
    send_order_ready_email.delay({
        "to": request.state.user["email"],
        "name": request.state.user["name"],
        "order_id": str(order.id)
    })

    return {"order": order}