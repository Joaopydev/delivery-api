from datetime import datetime, timezone
from enum import Enum
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey, LargeBinary, Enum as SQLEnum, DateTime, Numeric


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(LargeBinary)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def to_dict_necessary_attributes(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "active": self.active,
            "admin": self.admin
        }


class OrderStatus(Enum):
    PENDING: str = "pending"
    PREPARING: str = "preparing"
    AWAITING_CONFIRMATION: str = "awaiting confirmation"
    CANCELED: str = "canceled"
    COMPLETED: str = "completed"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, index=True)
    user: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal(0.00))
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    confirmed_on: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    estimated_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    order_ready_in: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", backref="current_order", cascade="all, delete-orphan", lazy="selectin")

    @property
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status.value,
            "price": self.price,
            "created_at": self.created_at,
            "confirmed_on": self.confirmed_on,
            "estimated_time": self.estimated_time,
            "order_ready_in": self.order_ready_in,
            "items": [item.to_dict for item in self.items],
        }

class ItemSize(Enum):
    SMALL: str = "small"
    AVERAGE: str = "average"
    BIG: str = "big"


class OrderItem(Base):

    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    flavor: Mapped[str] = mapped_column(String(200))
    size: Mapped[str] = mapped_column(SQLEnum(ItemSize))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    order: Mapped[Order] = mapped_column(ForeignKey("orders.id"), index=True)

    @property
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "quantity": self.quantity,
            "flavor": self.flavor,
            "size": self.size,
            "unit_price": self.unit_price,
            "order": self.order,
        }


class PaymentStatus(Enum):
    PENDING: str = "pending"
    PAID: str = "paid"
    CANCELED: str = "canceled"

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False, index=True)
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    related_order: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal(0.00))
