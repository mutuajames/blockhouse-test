"""
Pydantic schema models module.

This module defines the Pydantic models used for request and response validation.
These schemas ensure data validation and serialization/deserialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import OrderType, OrderStatus

class OrderBase(BaseModel):
    """
    Base schema for order data shared across requests and responses.
    
    This schema contains common fields used in different order-related operations.
    """
    symbol: str
    price: float = Field(gt=0)
    quantity: int = Field(gt=0)
    order_type: OrderType

class OrderCreate(OrderBase):
    """
    Schema for creating a new order.
    
    Inherits all fields from OrderBase with no additional fields,
    as all required fields for order creation are already in the base class.
    """
    pass

class OrderUpdate(BaseModel):
    """
    Schema for updating an existing order.
    
    Currently only allows updating the order status.
    """
    status: OrderStatus

class Order(OrderBase):
    """
    Schema for order responses with all order data including system fields.
    
    This schema includes all order fields that are returned by the API.
    """
    id: int
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class OrderList(BaseModel):
    """
    Schema for a list of orders with count information.
    
    Used for endpoints that return multiple orders.
    """
    orders: List[Order]
    count: int