from datetime import (
    datetime, timedelta, timezone
)
from typing import (
    Optional,
    List,
    Tuple,
)

from app.db.models.schemas import (
    Order,
    OrderStatus,
    User,
    OrderItem,
)
from app.schemas.order_schemas import (
    OrderSchema,
    OrderItemSchema,
)


from app.repository.order_repository import OrderRepository
from app.repository.account_repository import AccountRepository
from app.events.dispatcher import EventDispatcher

from app.core.exceptions import (
    OrderCancellationTimeExceededError,
    OrderDoesNotBelongToUserError,
    PermissionDeniedError,
    OrderItemDoesNotBelongToOrderError,
    OrderNotFoundError,
    OrderItemNotFoundError,
    UserNotFoundError,
)
from app.events.order_events import (
    OrderConfirmedEvent,
    OrderReadyEvent,
)


class OrderService:

    '''Service class to handle order-related operations.'''

    def __init__(
        self,
        account_repository: AccountRepository,
        order_repository: OrderRepository,
        event_dispatcher: EventDispatcher,
    ):
        self.account_repository = account_repository
        self.order_repository = order_repository
        self.event_dispatcher = event_dispatcher

    async def create_order(self, order_data: OrderSchema):
        order = await self.order_repository.create_order(order_data)
        return order

    async def cancel_order(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:
        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id,
        )
        if datetime.now(timezone.utc) - order.confirmed_on > timedelta(minutes=15) and not user.admin:
            raise OrderCancellationTimeExceededError()

        if order.user != user_id and not user.admin:
            raise OrderDoesNotBelongToUserError()

        await self.order_repository.cancel_order(order)

        return order

    async def list_orders(
        self,
        order_status: OrderStatus,
    ) -> List[Order]:

        orders = await self.order_repository.list_orders_by_status(order_status)
        return orders

    async def add_item_to_order(
        self,
        order_id: int,
        user_id: int,
        order_item_data: OrderItemSchema
    ) -> OrderItem:

        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id,
        )

        if order.user != user.id:
            raise PermissionDeniedError()

        order_item = await self.order_repository.add_item_to_order(order, order_item_data)
        return order_item

    async def delete_item_from_order(
        self,
        order_id: int,
        order_item_id: int,
        user_id: int,
    ) -> None:

        order, user, order_item = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id,
            order_item_id=order_item_id,
        )
        if order.user != user.id and not user.admin:
            raise PermissionDeniedError()

        if order_item.order != order.id:
            raise OrderItemDoesNotBelongToOrderError()

        await self.order_repository.delete_item_from_order(order_item)

    async def confirm_order(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:
        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id
        )
        if not user.admin:
            raise PermissionDeniedError()

        order = await self.order_repository.update_order_status(
            order=order,
            status=OrderStatus.PREPARING,
        )
        await self.event_dispatcher.dispatch(
            OrderConfirmedEvent(
                user_email=user.email,
                user_name=user.name,
                order_id=order.id,
                order=order.to_dict,
            )
        )

        return order

    async def confirm_order_readiness(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:

        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id
        )

        if not user.admin:
            raise PermissionDeniedError()

        order = await self.order_repository.update_order_status(
            order=order,
            status=OrderStatus.COMPLETED
        )
        await self.event_dispatcher.dispatch(
            OrderReadyEvent(
                user_email=user.email,
                user_name=user.name,
                order_id=order.id,
            )
        )
        return order

    async def send_order(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:
        order, user, _ = await self._ensure_entities_exists(
            order_id=order_id,
            user_id=user_id
        )
        if order.user != user.id and not user.admin:
            raise PermissionDeniedError()

        order = await self.order_repository.update_order_status(
            order=order,
            status=OrderStatus.AWAITING_CONFIRMATION,
        )
        return order

    async def _ensure_entities_exists(
        self,
        order_id: Optional[int] = None,
        user_id: Optional[int] = None,
        order_item_id: Optional[int] = None,
    ) -> Tuple[Optional[Order], Optional[User], Optional[OrderItem]]:

        order = await self.order_repository.get_order_by_id(order_id) if order_id else None
        if order_id and not order:
            raise OrderNotFoundError()

        user = await self.account_repository.get_account_by_id(user_id) if user_id else None
        if user_id and not user:
            raise UserNotFoundError()

        order_item = await self.order_repository.get_order_item_by_id(order_item_id) if order_item_id else None
        if order_item_id and not order_item:
            raise OrderItemNotFoundError()

        return order, user, order_item
