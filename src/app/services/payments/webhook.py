from typing import Dict, Any

import stripe

from app.repository.payment_repository import PaymentRepository
from app.db.models.schemas import PaymentStatus

from app.events.dispatcher import EventDispatcher
from app.events.order_events import ConfirmPaidOrderEvent

from app.integrations.payment_gateway.stripe_client import StripeClient
from app.core.exceptions import PaymentNotFoundError

class WebHookService:

    def __init__(
        self,
        payment_repository: PaymentRepository,
        event_dispatcher: EventDispatcher
    ):
        self.client = StripeClient()
        self.payment_repository = payment_repository
        self.event_dispatcher = event_dispatcher

    async def handler_webhook_event(self, payload, sig_header) -> Dict[str, Any]:
        event = self.client.webhook_construct_event(
            payload=payload,
            sig_header=sig_header,
        )
        await self._handler(event)

    async def _handler(self, event: stripe.Event):

        if event.type == "checkout.session.completed":
            session = event.data.object
            await self._handle_checkout_session(session)

    async def _handle_checkout_session(self, session: Dict[str, Any]) -> None:

        session_id = session["id"]
        customer_email = session.get('customer_details', {}).get('email')
        customer_name = session.get('customer_details', {}).get('name')

        payment = await self.payment_repository.get_payment_by_session_id(session_id=session_id)
        if not payment:
            raise PaymentNotFoundError()

        await self.payment_repository.update_payment_status(
            payment=payment,
            status=PaymentStatus.PAID
        )
        await self.event_dispatcher.dispatch(
            ConfirmPaidOrderEvent(
                user_email=customer_email,
                user_name=customer_name,
                order_id=payment.related_order,
            )
        )
