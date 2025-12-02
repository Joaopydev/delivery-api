from typing import List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from ..db.models.schemas import ItemSize


class CreateOrderSchema(BaseModel):
    user_id: int

class DeleteItemFromOrderSchema(BaseModel):
    id: int


class OrderItemSchema(BaseModel):
    quantity: int
    flavor: str
    size: ItemSize
    unit_price: float
    order: int

    class Config:
        from_attributes = True

class OrderSchema(BaseModel):
    id: int
    status: str
    user: int
    price: float
    date: datetime
    items: List[OrderItemSchema]

    class Config:
        from_attributes = True