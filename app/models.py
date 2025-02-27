"""
Database models module.

This module defines the SQLAlchemy ORM models for the database tables.
It includes order types, order statuses, and the Order model.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
import enum
from .database import Base

class OrderType(str, enum.Enum):
    """
    Enum representing different types of trading orders.
    
    Attributes:
        MARKET: Order executed immediately at current market price
        LIMIT: Order executed at specified price or better
        STOP: Order becomes market order when a specified price is reached
        STOP_LIMIT: Order becomes limit order when a specified price is reached
    """
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderStatus(str, enum.Enum):
    """
    Enum representing different states of an order.
    
    Attributes:
        PENDING: Order has been submitted but not processed
        FILLED: Order has been completely executed
        PARTIALLY_FILLED: Order has been partially executed
        CANCELLED: Order has been cancelled
        REJECTED: Order has been rejected by the system
    """
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class Order(Base):
    """
    SQLAlchemy model representing a trading order in the database.
    
    This model stores all information about a trading order including
    symbol, price, quantity, type, status, and timestamps.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    quantity = Column(Integer)
    order_type = Column(Enum(OrderType))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())