"""WebSocket connection manager using Redis pub/sub.

This module manages active WebSocket connections and provides helper
functions to broadcast threat alerts published via Redis. The manager
listens on a pub/sub channel and forwards messages to all connected
clients. Clients authenticate by providing a valid JWT in the
``token`` query parameter. See ``app.main`` for registration of the
WebSocket route.
"""

import asyncio
import json
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from .services.auth_service import get_current_user
from .db.redis_client import subscribe


class ConnectionManager:
    def __init__(self, channel: str = "threat_alerts") -> None:
        self.active_connections: Set[WebSocket] = set()
        self.channel = channel
        self.started = False

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        # Start listening to Redis once a connection is established
        if not self.started:
            asyncio.create_task(self._listen())
            self.started = True

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast(self, message: str) -> None:
        to_remove = []
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                to_remove.append(connection)
        for conn in to_remove:
            self.disconnect(conn)

    async def _listen(self) -> None:
        pubsub = await subscribe(self.channel)
        async for msg in pubsub.listen():
            if msg is None or msg.get("type") != "message":
                continue
            data = msg.get("data")
            if data:
                await self.broadcast(data)


manager = ConnectionManager()