from datetime import datetime
from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, LargeBinary, Enum as SQLEnum, DateTime


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
    CANCELED: str = "canceled"
    COMPLETED: str = "completed"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    price: Mapped[float] = mapped_column(Float, default=0.0)
    date: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.now)
    # items: 


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
    unit_price: Mapped[float] = mapped_column(Float)
    order: Mapped[Order] = mapped_column(ForeignKey("orders.id"))