from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.schemas import (
    Payment,
    PaymentStatus,
    Order,
)

class PaymentRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_payment(
        self,
        checkout_session_id: str,
        order: Order,
    ) -> None:

        new_payment = Payment(
            id=checkout_session_id,
            related_order=order.id,
            amount_paid=order.price,
        )
        self.session.add(new_payment)
        await self.session.flush()

    async def get_payment_by_session_id(self, session_id: str) -> Payment:
        payment = await self.session.get(Payment, session_id)
        return payment
    
    async def update_payment_status(self, payment: Payment, status: PaymentStatus) -> None:
        payment.status = status
        await self.session.flush()