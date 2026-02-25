from datetime import datetime, timedelta, timezone, time
from typing import Optional, List, Tuple
from sqlalchemy import select
from fastapi import HTTPException, status

from app.db.models.schemas import Order, OrderStatus, User, OrderItem
from app.schemas.order_schemas import OrderSchema, OrderItemSchema
from app.repository.order_repository import OrderRepository
from app.repository.account_repository import AccountRepository


class OrderService:

    '''Service class to handle order-related operations.'''

    def __init__(self, account_repository: AccountRepository, order_repository: OrderRepository):

        self.account_repository = account_repository
        self.order_repository = order_repository

    async def create_order(self, order_data: OrderSchema):
        order = await self.order_repository.create_order(order_data)
        return order
        
    async def cancel_order(
        self, 
        order_id: int, 
        user_id: int,
    ) -> Order:
        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id,
        )
        if datetime.now(timezone.utc) - order.confirmed_on > timedelta(min=15) and not user.admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The time allowed to cancel the order has already passed.",
            )

        if order.user != user_id and not user.admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The current user is not the order holder who wishes to cancel the order.",
            )
        await self.order_repository.cancel_order(order)
        
        return order
    
    async def list_orders(
        self,
        order_status: OrderStatus,
    ) -> List[Order]:
        
        orders = await self.order_repository.list_orders_by_status(order_status)
        return orders
    
    async def add_item_to_order(
        self,
        order_id: int,
        user_id: int,
        order_item_data: OrderItemSchema
    ) -> OrderItem:
        
        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id,
        )

        if order.user != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this order.",
            )
        
        order_item = await self.order_repository.add_item_to_order(order, order_item_data)
        return order_item
    
    async def delete_item_from_order(
        self,
        order_id: int,
        order_item_id: int,
        user_id: int,
    ) -> None:
        
        order, user, order_item = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id,
            order_item_id=order_item_id,
        )
        if order.user != user.id and not user.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this order.",
            )
        
        if order_item.order != order.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The order item does not belong to the specified order.",
            )
        
        await self.order_repository.delete_item_from_order(order_item)
    
    async def confirm_order(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:
        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id
        )
        if not user.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You do not have permission to modify this order"
            )
        order = await self.order_repository.update_order_status(
            order=order,
            status=OrderStatus.PREPARING,
        )

        return order
    
    async def confirm_order_readiness(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:
        
        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id
        )

        if not user.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You do not have permission to modify this order"
            )
        order = await self.order_repository.update_order_status(
            order=order,
            status=OrderStatus.COMPLETED
        )

        return order
        
    async def send_order(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:
        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id
        )
        if order.user != user.id and not user.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You do not have permission to modify this order"
            )
        
        order = await self.order_repository.update_order_status(
            order=order,
            status=OrderStatus.AWAITING_CONFIRMATION,
        )
        return order

    async def _ensure_entities_exists(
        self, 
        order_id: Optional[int] = None,
        user_id: Optional[int] = None,
        order_item_id: Optional[int] = None,
    ) -> Tuple[Optional[Order], Optional[User], Optional[OrderItem]]:
        
        order = await self.order_repository.get_order_by_id(order_id) if order_id else None
        if order_id and not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        
        user = await self.account_repository.get_account_by_id(user_id) if user_id else None
        if user_id and not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        order_item = await self.order_repository.get_order_item_by_id(order_item_id) if order_item_id else None
        if order_item_id and not order_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order item not found",
            )
        
        return order, user, order_item
