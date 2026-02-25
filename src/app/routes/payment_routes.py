from typing import Dict, Any
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.lib.token_jwt import verify_token
from app.utils.get_existing_order import order_exists

from app.services.payments.PaymentService import PaymentService
from app.db.models.schemas import Order
from app.db.connection import get_database

payment_router = APIRouter(prefix="/payments", tags=["payments"], dependencies=[Depends(verify_token)])

@payment_router.post("/create-checkout-session")
async def create_checkout_session(
    order: Order = Depends(order_exists),
    session: AsyncSession = Depends(get_database)
) -> Dict[str, Any]:

    payment_service = PaymentService(session=session)
    dic_checkout_url = await payment_service.create_checkout_session(order=order)
    return dic_checkout_url

@payment_router.get("/success")
async def payment_success(
    session_id: str,
    session: AsyncSession = Depends(get_database)
) -> Dict[str, Any]:

    payment_service = PaymentService(session=session)
    status = await payment_service.payment_success(session_id=session_id)
    return status

@payment_router.get("/cancel")
async def payment_cancel() -> Dict[str, Any]:
    return {"message": "Payment has been canceled"}