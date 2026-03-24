from typing import Dict, Any
from decimal import Decimal

from app.db.models.schemas import Order, PaymentStatus
from app.repository.payment_repository import PaymentRepository
from app.integrations.payment_gateway.stripe_client import StripeClient
from app.integrations.payment_gateway.stripe_config import settings

from app.core.exceptions import (
    OrderEqualToZeroError,
    PaymentNotFoundError,
)

class PaymentService:

    def __init__(self, payment_repository: PaymentRepository):
        self.client = StripeClient()
        self.payment_repository = payment_repository

    async def create_checkout_session(self, order: Order) -> Dict[str, Any]:

        if order.price <= 0:
            raise OrderEqualToZeroError()

        payment_config = {
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price_data": {
                        "currency": "brl",
                        "product_data": {
                            "name": order.id
                        },
                        "unit_amount": int(Decimal(str(order.price)) * 100)
                    },
                    "quantity": 1
                }
            ],
            "mode": "payment",
            "success_url": f"{settings.domain}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{settings.domain}/payments/cancel"
        }
        checkout_session = await self.client.create_checkout_session(data=payment_config)

        await self.payment_repository.create_payment(
            checkout_session_id=checkout_session.id,
            order=order
        )

        return {"checkout_url": checkout_session.url}


    async def payment_success(self, session_id: str) -> Dict[str, str]:
        payment = await self.payment_repository.get_payment_by_session_id(session_id=session_id)
        if not payment:
            raise PaymentNotFoundError()

        session = await self.client.retrieve_checkout_session(session_id=session_id)

        if payment.status == PaymentStatus.PAID:
            return {"status": "already_paid"}

        if session.payment_status == "paid":
            return {"status": "success"}

        return {"status": "pending"}
