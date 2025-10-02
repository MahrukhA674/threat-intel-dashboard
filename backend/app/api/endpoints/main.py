"""FastAPI application entry point.

This module creates the FastAPI app, registers routers, configures
CORS, mounts the WebSocket endpoint and schedules background tasks.
"""

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from .auth import auth as auth_router
from .threats import threats as threats_router
from ...tasks import monitor_new_threats, ingest_feeds
from ...websocket import manager



app = FastAPI(title="Threat Intelligence Dashboard API")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router.router)
app.include_router( threats_router.router, prefix="/api")


@app.on_event("startup")
async def startup_event() -> None:
    """Schedule the background monitor task on startup."""
    asyncio.create_task(monitor_new_threats())
    asyncio.create_task(ingest_feeds())


@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle incoming WebSocket connections for threat alerts."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection open by receiving data
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)