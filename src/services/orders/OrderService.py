from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query
from sqlalchemy import select
from sqlalchemy.sql import func
from fastapi import HTTPException, status

from ...db.models.schemas import Order, User
from ...schemas.order_schemas import OrderSchema
from ...db.models.schemas import OrderStatus


class OrderService:

    def __init__(self, session: Optional[AsyncSession]):
        self.session = session

    async def create_order(self, order_data: OrderSchema):
        new_order = Order(user=order_data.user_id)
        self.session.add(new_order)
        await self.session.commit()
        await self.session.refresh(new_order)

        return new_order
        
    async def cancel_order(self, order_id: int, user_id: int) -> Order:
        query = select(Order).where(Order.id == order_id)
        result = await self.session.execute(query)
        order = result.scalars().first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order not found",
            )
        
        query_fetch_user = select(User).where(User.id == user_id)
        fetch_user_result = await self.session.execute(query_fetch_user)
        user = fetch_user_result.scalars().first()

        if order.user != user_id and not user.admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The current user is not the order holder who wishes to cancel the order.",
            )
        
        order.status = OrderStatus.CANCELED
        await self.session.commit()
        await self.session.refresh(order)
        
        return order
    
    async def list_orders(self, user_id, start_date: str, end_date: str) -> List[Order]:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()

        if not user.admin:
            raise HTTPException(
                detail="Unauthorized user",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        
        query = select(Order)
        query = self._filter_orders_by_date(
            query=query,
            start_date=start_date,
            end_date=end_date,
        )
        result = await self.session.execute(query)
        orders = result.scalars().all()

        return orders

    def _filter_orders_by_date(self, query: Query, start_date: str, end_date: str) -> Query:
        if start_date:
            query = query.filter(func.date(Order.date) >= start_date)
        if end_date:
            query = query.filter(func.date(Order.date) <= end_date)
        return query
        
