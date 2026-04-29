"""WebSocket handler for progress updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.job import ProgressMessage, TaskStatus, ProductType
import asyncio
import json

websocket_router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections per job."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if job_id in self.active_connections:
            self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def broadcast(self, job_id: str, message: ProgressMessage):
        """Broadcast progress message to all connections for a job."""
        if job_id not in self.active_connections:
            return

        message_json = message.model_dump_json()
        dead_connections = []

        for connection in self.active_connections[job_id]:
            try:
                await connection.send_text(message_json)
            except Exception:
                dead_connections.append(connection)

        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(job_id, connection)


manager = ConnectionManager()


@websocket_router.websocket("/job/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await manager.connect(job_id, websocket)

    try:
        while True:
            # Keep connection alive, wait for client messages
            data = await websocket.receive_text()

            # Echo back for testing
            # In production, this would receive commands or just keep alive
            await websocket.send_text(json.dumps({"type": "ack", "job_id": job_id}))

    except WebSocketDisconnect:
        manager.disconnect(job_id, websocket)


async def push_progress(
    job_id: str,
    task_type: ProductType,
    status: TaskStatus,
    progress: int,
    message: str = None,
    error: str = None,
    download_url: str = None,
):
    """Push progress update to all WebSocket clients for a job."""
    progress_msg = ProgressMessage(
        job_id=job_id,
        task_type=task_type,
        status=status,
        progress=progress,
        message=message,
        error=error,
        download_url=download_url,
    )
    await manager.broadcast(job_id, progress_msg)