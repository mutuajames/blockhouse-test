"""
Routes module.

This module defines all the API endpoints related to orders.
It handles order creation, retrieval, and status updates.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Set
import json

from .. import models, schemas, database
from ..websocket.order_updates import order_update_manager

router = APIRouter()

@router.post("/orders", response_model=schemas.Order, status_code=201)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db),
                background_tasks: BackgroundTasks = None):
    db_order = models.Order(
        symbol=order.symbol,
        price=order.price,
        quantity=order.quantity,
        order_type=order.order_type,
        status=models.OrderStatus.PENDING
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Notify WebSocket clients about the new order
    if background_tasks:
        background_tasks.add_task(
            order_update_manager.broadcast_order_update, 
            "NEW_ORDER", 
            {
                "id": db_order.id,
                "symbol": db_order.symbol,
                "status": db_order.status
            }
        )
    
    return db_order

@router.get("/orders", response_model=schemas.OrderList)
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return {"orders": orders, "count": len(orders)}

@router.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(database.get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.patch("/orders/{order_id}", response_model=schemas.Order)
def update_order_status(order_id: int, order_update: schemas.OrderUpdate, 
                       db: Session = Depends(database.get_db),
                       background_tasks: BackgroundTasks = None):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_order.status = order_update.status
    db.commit()
    db.refresh(db_order)
    
    # Notify WebSocket clients about the status update
    if background_tasks:
        background_tasks.add_task(
            order_update_manager.broadcast_order_update, 
            "STATUS_UPDATE", 
            {
                "id": db_order.id,
                "symbol": db_order.symbol,
                "status": db_order.status
            }
        )
    
    return db_order