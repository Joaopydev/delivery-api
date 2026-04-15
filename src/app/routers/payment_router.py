from typing import Dict, Any
from fastapi import APIRouter, Depends

from app.lib.token_jwt import verify_token
from app.utils.get_existing_order import order_exists

from app.db.models.schemas import Order
from app.dependencies.payment_dependencies import get_payment_service
from app.services.payments.payment import PaymentService

payment_router = APIRouter(prefix="/payments", tags=["payments"], dependencies=[Depends(verify_token)])

@payment_router.post("/create-checkout-session")
async def create_checkout_session(
    order: Order = Depends(order_exists),
    payment_service: PaymentService = Depends(get_payment_service),
) -> Dict[str, Any]:

    dic_checkout_url = await payment_service.create_checkout_session(order=order)
    return dic_checkout_url

@payment_router.get("/success")
async def payment_success(
    session_id: str,
    payment_service: PaymentService = Depends(get_payment_service)
) -> Dict[str, Any]:

    status = await payment_service.payment_success(session_id=session_id)
    return status

@payment_router.get("/cancel")
async def payment_cancel() -> Dict[str, Any]:
    return {"message": "Payment has been canceled"}
