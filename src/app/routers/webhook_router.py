from fastapi import APIRouter, Request, Depends

from app.services.payments.webhook import WebHookService
from app.dependencies.payment_dependencies import get_webhook_service


webhook_router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@webhook_router.post("/webhook")
async def receive_webhook(
    request: Request,
    webhook_service: WebHookService = Depends(get_webhook_service),
) -> None:
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    await webhook_service.handler_webhook_event(
        payload=payload,
        sig_header=sig_header,
    )
