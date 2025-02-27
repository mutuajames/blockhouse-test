from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio

class OrderUpdateManager:
    """
    Manager for WebSocket connections and order update broadcasts.
    
    This class maintains a list of active WebSocket connections and handles
    subscribing clients to specific symbols and broadcasting updates.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_symbols: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket, symbols: List[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if symbols:
            self.client_symbols[websocket] = set(symbols)
        else:
            self.client_symbols[websocket] = set()  # Subscribe to all symbols

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.client_symbols:
            del self.client_symbols[websocket]

    async def broadcast_order_update(self, update_type: str, order_data: dict):
        """
        Broadcast an order update to all relevant connected clients.
        
        Args:
            update_type: Type of update (e.g., NEW_ORDER, STATUS_UPDATE)
            order_data: Order data to broadcast
        """
        for connection in self.active_connections:
            symbols = self.client_symbols.get(connection, set())
            # Send update if client is subscribed to all symbols or to this specific symbol
            if not symbols or order_data.get("symbol") in symbols:
                message = {
                    "type": update_type,
                    "data": order_data
                }
                await connection.send_text(json.dumps(message))

    async def subscribe_to_symbols(self, websocket: WebSocket, symbols: List[str]):
        """
        Subscribe a client to specific symbols.
        
        Args:
            websocket: The WebSocket connection to update
            symbols: List of symbols to subscribe to
        """
        if websocket in self.client_symbols:
            self.client_symbols[websocket].update(symbols)
        else:
            self.client_symbols[websocket] = set(symbols)

    async def unsubscribe_from_symbols(self, websocket: WebSocket, symbols: List[str]):
        """
        Unsubscribe a client from specific symbols.
        
        Args:
            websocket: The WebSocket connection to update
            symbols: List of symbols to unsubscribe from
        """
        if websocket in self.client_symbols:
            self.client_symbols[websocket] = self.client_symbols[websocket] - set(symbols)

order_update_manager = OrderUpdateManager()