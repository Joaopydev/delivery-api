from typing import Dict, Any

import stripe

from fastapi import HTTPException

from app.services.payments.PaymentService import settings
from app.repository.payment_repository import PaymentRepository
from app.db.models.schemas import PaymentStatus
from src.tasks.emails.send_email import confirm_paid_order

class WebHookService:

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    def builder_webhook_event(self, payload, sig_header) -> Dict[str, Any]:
        try:
            return stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.stripe_webhook_secret,
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
    async def handler(self, event: stripe.Event):

        if event.type == "checkout.session.completed":
            session = event.data.object
            await self._handle_checkout_session(session)
    
    async def _handle_checkout_session(self, session: Dict[str, Any]) -> None:

        session_id = session["id"]
        customer_email = session.get('customer_details', {}).get('email')
        customer_name = session.get('customer_details', {}).get('name')

        payment = await self.payment_repository.get_payment_by_session_id(session_id=session_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        await self.payment_repository.update_payment_status(
            payment=payment,
            status=PaymentStatus.PAID
        )

        confirm_paid_order.delay({
            "to": customer_email,
            "name": customer_name,
            "order_id": str(payment.related_order)
        })

