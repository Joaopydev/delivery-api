from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.schemas import Order
from ...schemas.order_schemas import OrderSchema


class OrderService:

    def __init__(self, session: Optional[AsyncSession]):
        self.session = session

    async def create_order(self, order_data: OrderSchema):
        async with session as session:
            new_order = Order(user=order_data.user_id)
            session.add(new_order)
            await session.commit()
            await session.refresh(new_order)

            return new_order