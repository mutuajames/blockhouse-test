from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio

class OrderUpdateManager:
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
        if websocket in self.client_symbols:
            self.client_symbols[websocket].update(symbols)
        else:
            self.client_symbols[websocket] = set(symbols)

    async def unsubscribe_from_symbols(self, websocket: WebSocket, symbols: List[str]):
        if websocket in self.client_symbols:
            self.client_symbols[websocket] = self.client_symbols[websocket] - set(symbols)

order_update_manager = OrderUpdateManager()