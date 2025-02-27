"""
Main application module.

This is the entry point of the FastAPI application.
It configures the API, includes routers, and sets up WebSocket handlers.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json

from .database import engine, Base
from .routes import orders
from .websocket.order_updates import order_update_manager

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trading API",
    description="A simple trading order management API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(orders.router, tags=["orders"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Trading API"}

@app.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    """
    WebSocket endpoint for real-time order updates.
    
    This endpoint allows clients to:
    1. Connect and receive real-time order updates
    2. Subscribe to specific trading symbols
    3. Unsubscribe from specific trading symbols
    
    Args:
        websocket: The WebSocket connection object
    """
    await order_update_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle subscription requests
            if message.get("action") == "subscribe" and "symbols" in message:
                await order_update_manager.subscribe_to_symbols(websocket, message["symbols"])
            elif message.get("action") == "unsubscribe" and "symbols" in message:
                await order_update_manager.unsubscribe_from_symbols(websocket, message["symbols"])
                
    except WebSocketDisconnect:
        order_update_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        order_update_manager.disconnect(websocket)

# If this file is executed directly, run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)