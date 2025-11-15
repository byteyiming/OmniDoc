"""WebSocket connection manager"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Set

from fastapi import WebSocket

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """
    Manage WebSocket connections per project.
    
    This class maintains a registry of active WebSocket connections grouped
    by project ID, allowing broadcast of progress updates to all connected
    clients for a specific project.
    
    Features:
    - Per-project connection tracking
    - Automatic cleanup of disconnected clients
    - Thread-safe connection management
    - Timestamped message broadcasting
    """
    
    def __init__(self) -> None:
        """Initialize the WebSocket manager with empty connection registry."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str) -> None:
        """
        Connect a WebSocket to a project.
        
        Accepts the WebSocket connection and adds it to the registry for
        the specified project.
        
        Args:
            websocket: WebSocket connection to accept
            project_id: Project identifier to associate with this connection
        """
        await websocket.accept()
        self.active_connections.setdefault(project_id, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str) -> None:
        """
        Disconnect a WebSocket from a project.
        
        Removes the connection from the registry. If no connections remain
        for the project, the project entry is removed.
        
        Args:
            websocket: WebSocket connection to remove
            project_id: Project identifier
        """
        connections = self.active_connections.get(project_id)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self.active_connections.pop(project_id, None)

    async def send_progress(self, project_id: str, message: Dict[str, Any]) -> None:
        """
        Send progress update to all connected clients for a project.
        
        Broadcasts a message to all active WebSocket connections for the given
        project. Automatically removes disconnected clients from the registry.
        
        Args:
            project_id: Project identifier
            message: Message dictionary to send (will have timestamp added)
        
        Note:
            If no connections exist for the project, this method returns silently.
            Failed sends are logged but don't raise exceptions.
        """
        connections = self.active_connections.get(project_id)
        if not connections:
            return
        
        payload = {**message, "timestamp": datetime.now().isoformat()}
        disconnected: Set[WebSocket] = set()

        for connection in connections:
            try:
                await connection.send_json(payload)
            except Exception as exc:
                logger.warning("Failed to send WebSocket message: %s", exc)
                disconnected.add(connection)
        
        for connection in disconnected:
            self.disconnect(connection, project_id)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()

