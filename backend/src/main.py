"""Nexus — AI Agent Mission Control.

FastAPI application with REST API + WebSocket for real-time monitoring.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.routes import router
from .api.websocket import manager
from .db.database import init_db

_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Nexus — AI Agent Mission Control",
    description="Multi-model agent team orchestration with real-time monitoring",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router)


# ── WebSocket endpoint ─────────────────────────────────────────────


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # Echo or handle client messages
            await ws.send_text(f'{{"type":"ack","data":"{data}"}}')
    except WebSocketDisconnect:
        manager.disconnect(ws)


# ── Root ───────────────────────────────────────────────────────────


@app.get("/")
async def root():
    return {
        "name": "Nexus",
        "version": "0.1.0",
        "description": "AI Agent Mission Control",
        "docs": "/docs",
        "uptime_seconds": round(time.time() - _start_time, 1),
    }


# ── Serve static frontend (production) ────────────────────────────

_static_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")
