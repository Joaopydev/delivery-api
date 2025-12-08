from datetime import datetime
from enum import Enum
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey, LargeBinary, Enum as SQLEnum, DateTime, Numeric


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(LargeBinary)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)


class OrderStatus(Enum):
    PENDING: str = "pending"
    PREPARING: str = "preparing"
    AWAITING_CONFIRMATION: str = "awaiting confirmation"
    CANCELED: str = "canceled"
    COMPLETED: str = "completed"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal(0.00))
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.now)
    confirmed_on: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=True)
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", backref="current_order", cascade="all, delete-orphan", lazy="selectin")


class ItemSize(Enum):
    SMALL: str = "small"
    AVERAGE: str = "average"
    BIG: str = "big"


class OrderItem(Base):

    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer)
    flavor: Mapped[str] = mapped_column(String(200))
    size: Mapped[str] = mapped_column(SQLEnum(ItemSize))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    order: Mapped[Order] = mapped_column(ForeignKey("orders.id"))


# TODO Implement Kitchen Table



# TODO Implement Payments Table