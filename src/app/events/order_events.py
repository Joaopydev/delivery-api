from typing import Dict, Any, Optional
from datetime import datetime, timezone
from uuid import uuid4


class BaseOrderEvent:
    def __init__(
        self,
        user_email: str,
        user_name: str,
        order_id: int,
        order: Optional[Dict[str, Any]] = None,
    ):
        self.id = str(uuid4())
        self.timestamp = datetime.now(timezone.utc)
        self.user_email = user_email
        self.user_name = user_name
        self.order_id = order_id
        self.order = order


class OrderConfirmedEvent(BaseOrderEvent):
    pass


class OrderReadyEvent(BaseOrderEvent):
    pass


class ConfirmPaidOrderEvent(BaseOrderEvent):
    pass


class OrderPaymentFailedEvent(BaseOrderEvent):
    pass
