from sqlalchemy import event, select, func
from ..db.models.schemas import Order, OrderItem

print("Registering order item event listeners.")

def execute_order_item_event(mapper, connection, target):
    order_id = target.order

    subquery = (
        select(func.sum(OrderItem.unit_price * OrderItem.quantity))
        .where(OrderItem.order == order_id)
    )

    total = connection.execute(subquery).scalar() or 0.0

    update_query = (
        Order.__table__.update()
        .where(Order.id == order_id)
        .values(price=total)
    )

    connection.execute(update_query)

event.listen(OrderItem, 'after_insert', execute_order_item_event)
event.listen(OrderItem, 'after_delete', execute_order_item_event)
event.listen(OrderItem, 'after_update', execute_order_item_event)