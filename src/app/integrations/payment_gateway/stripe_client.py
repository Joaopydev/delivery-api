import stripe
from app.integrations.payment_gateway.stripe_config import settings
from app.core.exceptions import (
    InvalidPayloadError,
    InvalidSignatureError,
    PaymentNotFoundError,
    BusinessException,
)

stripe.api_key = settings.stripe_secret_key


class StripeClient:

    @staticmethod
    async def create_checkout_session(data: dict) -> stripe.checkout.Session:
        try:
            return await stripe.checkout.Session.create_async(**data)
        except stripe.error.InvalidRequestError as exc:
            raise InvalidPayloadError(detail="Invalid Stripe checkout session data") from exc
        except stripe.error.AuthenticationError as exc:
            raise BusinessException(detail="Stripe authentication failed") from exc
        except stripe.error.PermissionError as exc:
            raise BusinessException(detail="Stripe permission denied") from exc
        except (stripe.error.APIConnectionError, stripe.error.RateLimitError, stripe.error.APIError) as exc:
            raise BusinessException(detail="Stripe service temporarily unavailable") from exc
        except stripe.error.StripeError as exc:
            raise BusinessException(detail="Unexpected Stripe error") from exc

    @staticmethod
    async def retrieve_checkout_session(session_id: str) -> stripe.checkout.Session:
        try:
            return await stripe.checkout.Session.retrieve_async(session_id)
        except stripe.error.InvalidRequestError as exc:
            raise PaymentNotFoundError(detail="Stripe checkout session not found") from exc
        except stripe.error.AuthenticationError as exc:
            raise BusinessException(detail="Stripe authentication failed") from exc
        except stripe.error.PermissionError as exc:
            raise BusinessException(detail="Stripe permission denied") from exc
        except (stripe.error.APIConnectionError, stripe.error.RateLimitError, stripe.error.APIError) as exc:
            raise BusinessException(detail="Stripe service unavailable, please try again later") from exc
        except stripe.error.StripeError as exc:
            raise BusinessException(detail="Unexpected Stripe error") from exc

    @staticmethod
    async def webhook_construct_event(payload: bytes, sig_header: str) -> stripe.Event:

        try:
            return stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.stripe_webhook_secret,
            )
        except ValueError as exc:
            raise InvalidPayloadError() from exc
        except stripe.error.SignatureVerificationError as exc:
            raise InvalidSignatureError() from exc
