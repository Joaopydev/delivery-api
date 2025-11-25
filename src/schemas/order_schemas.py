from datetime import datetime
from pydantic import BaseModel


class CreateOrderSchema(BaseModel):
    user_id: int

class OrderSchema(BaseModel):
    id: int
    status: str
    user: int
    price: float
    date: datetime

    class Config:
        from_attributes = True  