from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query
from sqlalchemy import select
from sqlalchemy.sql import func
from fastapi import HTTPException, status

from ...db.models.schemas import Order, User, OrderItem
from ...schemas.order_schemas import OrderSchema, OrderItemSchema, DeleteItemFromOrderSchema
from ...db.models.schemas import OrderStatus


class OrderService:

    '''Service class to handle order-related operations.'''

    def __init__(self, session: Optional[AsyncSession]):
        self.session = session

    async def create_order(self, order_data: OrderSchema):
        new_order = Order(user=order_data.user_id)
        self.session.add(new_order)
        await self.session.commit()
        await self.session.refresh(new_order)

        return new_order
        
    async def cancel_order(
        self, 
        order_id: int, 
        user_id: int,
    ) -> Order:
        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id,
        )
        if order.user != user_id and not user.admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The current user is not the order holder who wishes to cancel the order.",
            )
        
        order.status = OrderStatus.CANCELED
        await self.session.commit()
        await self.session.refresh(order)
        
        return order
    
    async def list_orders(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[Order]:

        if end_date and start_date and end_date < start_date:
            raise HTTPException(
                detail="The end date cannot be earlier than the start date.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        user = await self.session.get(User, user_id)
        if not user.admin:
            raise HTTPException(
                detail="Unauthorized user",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
                
        if start_date is None and end_date is None:
            return []
        
        query = select(Order)
        query = self._filter_orders_by_date(
            query=query,
            start_date=start_date,
            end_date=end_date,
        )
        result = await self.session.execute(query)
        orders = result.scalars().all()

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
        
        order_item = OrderItem(
            quantity=order_item_data.quantity,
            flavor=order_item_data.flavor,
            size=order_item_data.size,
            unit_price=order_item_data.unit_price,
            order=order.id,
        )
        self.session.add(order_item)
        await self.session.commit()
        await self.session.refresh(order_item)

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
        
        await self.session.delete(order_item)
        await self.session.commit()
    

    async def _ensure_entities_exists(
        self, order_id: Optional[int] = None,
        user_id: Optional[int] = None,
        order_item_id: Optional[int] = None,
    ) -> Tuple[Optional[Order], Optional[User], Optional[OrderItem]]:
        
        order = await self.session.get(Order, order_id) if order_id else None
        if order_id and not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        
        user = await self.session.get(User, user_id) if user_id else None
        if user_id and not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        order_item = await self.session.get(OrderItem, order_item_id) if order_item_id else None
        if order_item_id and not order_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order item not found",
            )
        
        return order, user, order_item


    def _filter_orders_by_date(self, query: Query, start_date: str, end_date: str) -> Query:
        if start_date:
            query = query.filter(func.date(Order.date) >= start_date)
        if end_date:
            query = query.filter(func.date(Order.date) <= end_date)
        return query
    
    
        
