from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import OrderType, OrderStatus

class OrderBase(BaseModel):
    symbol: str
    price: float = Field(gt=0)
    quantity: int = Field(gt=0)
    order_type: OrderType

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: OrderStatus

class Order(OrderBase):
    id: int
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class OrderList(BaseModel):
    orders: List[Order]
    count: int