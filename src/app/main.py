#pylint: disable=wildcard-import, redefined-outer-name, unused-import, unused-argument, unused-wildcard-import
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers.auth_router import auth_router
from app.routers.order_router import order_router
from app.routers.payment_router import payment_router
from app.db.events_listeners.order_listeners import * # to register the event listeners

from app.events.dispatcher_instance import dispatcher
from app.events.handlers.order_handlers import (
    order_confirmed_handler,
    order_ready_handler,
    order_confirm_paid_handler,
)
from app.events.order_events import (
    OrderConfirmedEvent,
    OrderReadyEvent,
    ConfirmPaidOrderEvent,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    dispatcher.register_handler(OrderConfirmedEvent, order_confirmed_handler)
    dispatcher.register_handler(OrderReadyEvent, order_ready_handler)
    dispatcher.register_handler(ConfirmPaidOrderEvent, order_confirm_paid_handler)

    yield

app = FastAPI(
    title="Delivery API",
    description="API for managing orders, payments and delivery of a food delivery service.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(order_router)
app.include_router(auth_router)
app.include_router(payment_router)
