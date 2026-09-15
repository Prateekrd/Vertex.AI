"""WebSocket connection manager for live progress updates."""
from __future__ import annotations

import json
import asyncio
from typing import Dict, List, Any
from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections and broadcasts progress messages."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.progress_queues: Dict[str, asyncio.Queue] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            try:
                self.active_connections[job_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def send_progress(self, job_id: str, message: Dict[str, Any]):
        """Send a message to all connected clients for a job."""
        if job_id in self.active_connections:
            text = json.dumps(message, default=str)
            disconnected = []
            for ws in self.active_connections[job_id]:
                try:
                    await ws.send_text(text)
                except Exception:
                    disconnected.append(ws)
            for ws in disconnected:
                self.disconnect(ws, job_id)


ws_manager = ConnectionManager()
