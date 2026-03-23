import stripe

from app.integrations.payment_gateway.stripe_config import settings

stripe.api_key = settings.stripe_secret_key


class StripeClient:

    @staticmethod
    async def create_checkout_session(data: dict) -> stripe.checkout.Session:
        return await stripe.checkout.Session.create_async(**data)

    @staticmethod
    async def retrieve_checkout_session(session_id: str) -> stripe.checkout.Session:
        return await stripe.checkout.Session.retrieve_async(session_id)

    @staticmethod
    async def webhook_construct_event(payload: bytes, sig_header: str) -> stripe.Event:
        return stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.stripe_webhook_secret,
        )
