from datetime import datetime, timezone, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.schemas import OrderItem, Order, OrderStatus
from app.schemas.order_schemas import OrderSchema, OrderItemSchema

class OrderRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order_data: OrderSchema):
        
        new_order = Order(user=order_data.user_id)
        self.session.add(new_order)
        await self.session.flush()

        return new_order
    
    async def get_order_by_id(self, order_id: int) -> Order:
        order = await self.session.get(Order, order_id)
        return order
    
    async def get_order_item_by_id(self, order_item_id: int) -> OrderItem:
        order_item = await self.session.get(OrderItem, order_item_id)
        return order_item
    
    async def cancel_order(self, order: Order):

        order.status = OrderStatus.CANCELED
        await self.session.flush()

    async def add_item_to_order(self, order: Order, order_item_data: OrderItemSchema) -> OrderItem:

        order_item = OrderItem(
            quantity=order_item_data.quantity,
            flavor=order_item_data.flavor,
            size=order_item_data.size,
            unit_price=order_item_data.unit_price,
            order=order.id,
        )

        self.session.add(order_item)
        await self.session.flush()

        return order_item
    
    async def delete_item_from_order(self, order_item: OrderItem):

        await self.session.delete(order_item)
        await self.session.flush()
        
    async def update_order_status(self, order: Order, status: OrderStatus):

        if status == OrderStatus.PREPARING:
            order.confirmed_on = datetime.now(tz=timezone.utc)
        elif status == OrderStatus.COMPLETED:
            order.order_ready_in = datetime.now(tz=timezone.utc)

        order.status = status
        await self.session.flush()

        return order


    async def list_orders_by_status(self, order_status: OrderStatus):

        today = datetime.now(tz=timezone.utc)
        
        query = (
            select(Order)
            .where(
                Order.status == order_status,
                Order.created_at >= datetime.combine(today, time.min),
                Order.created_at <= datetime.combine(today, time.max)
            )
        )
        result = await self.session.execute(query)
        orders = result.scalars().all()

        return orders