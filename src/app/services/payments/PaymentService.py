from typing import Dict, Any, Optional
from decimal import Decimal
from pydantic_settings import BaseSettings, SettingsConfigDict

import stripe
from fastapi import HTTPException, status

from app.db.models.schemas import Order, Payment, PaymentStatus
from app.repository.payment_repository import PaymentRepository

class Settings(BaseSettings):
    stripe_secret_key: str
    stripe_publishable_key: str
    stripe_webhook_secret: str
    domain: str = "http://127.0.0.1:8000/"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
stripe.api_key = settings.stripe_secret_key

class PaymentService:

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
    
    async def create_checkout_session(self, order: Order) -> Dict[str, Any]:

        if order.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order value equal to or less than zero",
            )
        
        try:
            checkout_session = await stripe.checkout.Session.create_async(
                payment_method_types=["card"],
                line_items=[
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
                mode="payment",
                success_url=f"{settings.domain}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.domain}/payments/cancel"
            )

            await self.payment_repository.create_payment(
                checkout_session_id=checkout_session.id,
                order=order
            )

            return {"checkout_url": checkout_session.url}
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
    async def payment_success(self, session_id: str) -> Dict[str, str]:
        try:
            payment = await self.payment_repository.get_payment_by_session_id(session_id=session_id)
            session = await stripe.checkout.Session.retrieve_async(session_id)

            if payment.status == PaymentStatus.PAID:
                return {"status": "already_paid"}

            if session.payment_status == "paid":
                return {"status": "success"}
            
            return {"status": "pending"}
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )