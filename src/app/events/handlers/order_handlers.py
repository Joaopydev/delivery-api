from app.events.order_events import (
    OrderConfirmedEvent,
    OrderReadyEvent,
    ConfirmPaidOrderEvent,
)

from tasks.ai.generate_response import estimate_order_time
from tasks.emails.send_email import (
    send_confirmation_email,
    send_order_ready_email,
    confirm_paid_order,
)


def order_confirmed_handler(event: OrderConfirmedEvent):
    send_confirmation_email.delay({
        "to": event.user_email,
        "name": event.user_name,
        "order_id": str(event.order_id)
    })
    estimate_order_time.delay({
        "target_order": event.order
    })


def order_ready_handler(event: OrderReadyEvent):
    send_order_ready_email.delay({
        "to": event.user_email,
        "name": event.user_name,
        "order_id": str(event.order_id)
    })


def order_confirm_paid_handler(event: ConfirmPaidOrderEvent):
    confirm_paid_order.delay({
        "to": event.user_email,
        "name": event.user_name,
        "order_id": str(event.order_id)
    })
