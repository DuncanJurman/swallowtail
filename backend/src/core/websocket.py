"""WebSocket management for real-time updates."""

import logging
from typing import Dict, Set, Optional, Any
from uuid import UUID
import json

import socketio
from socketio import AsyncServer

from src.core.config import get_settings

logger = logging.getLogger(__name__)

# Create Socket.io server instance
sio = AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=get_settings().cors_origins,
    logger=True,
    engineio_logger=False
)

# Track connected clients by instance
connected_clients: Dict[str, Set[str]] = {}  # instance_id -> set of session_ids


class WebSocketManager:
    """Manages WebSocket connections and broadcasts."""
    
    def __init__(self, socketio_server: AsyncServer = sio):
        self.sio = socketio_server
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up Socket.io event handlers."""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle client connection."""
            logger.info(f"Client {sid} connected")
            # Store connection metadata if needed
            await self.sio.save_session(sid, {'connected_at': 'now'})
            return True  # Accept connection
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection."""
            logger.info(f"Client {sid} disconnected")
            # Clean up client from all instance rooms
            for instance_id, clients in connected_clients.items():
                if sid in clients:
                    clients.remove(sid)
                    await self.sio.leave_room(sid, f"instance_{instance_id}")
        
        @self.sio.event
        async def subscribe_instance(sid, data):
            """Subscribe to instance updates."""
            try:
                instance_id = data.get('instance_id')
                if not instance_id:
                    await self.sio.emit('error', {'message': 'instance_id required'}, to=sid)
                    return
                
                # Join instance room
                room = f"instance_{instance_id}"
                await self.sio.enter_room(sid, room)
                
                # Track client
                if instance_id not in connected_clients:
                    connected_clients[instance_id] = set()
                connected_clients[instance_id].add(sid)
                
                logger.info(f"Client {sid} subscribed to instance {instance_id}")
                await self.sio.emit('subscribed', {'instance_id': instance_id}, to=sid)
                
            except Exception as e:
                logger.error(f"Error subscribing client {sid}: {e}")
                await self.sio.emit('error', {'message': str(e)}, to=sid)
        
        @self.sio.event
        async def unsubscribe_instance(sid, data):
            """Unsubscribe from instance updates."""
            try:
                instance_id = data.get('instance_id')
                if not instance_id:
                    return
                
                # Leave instance room
                room = f"instance_{instance_id}"
                await self.sio.leave_room(sid, room)
                
                # Remove from tracking
                if instance_id in connected_clients:
                    connected_clients[instance_id].discard(sid)
                
                logger.info(f"Client {sid} unsubscribed from instance {instance_id}")
                await self.sio.emit('unsubscribed', {'instance_id': instance_id}, to=sid)
                
            except Exception as e:
                logger.error(f"Error unsubscribing client {sid}: {e}")
    
    async def broadcast_task_update(self, instance_id: str, task_id: str, update_data: Dict[str, Any]):
        """Broadcast task update to all clients subscribed to an instance."""
        room = f"instance_{instance_id}"
        
        event_data = {
            'instance_id': instance_id,
            'task_id': task_id,
            'type': 'task_update',
            'data': update_data
        }
        
        await self.sio.emit('task_update', event_data, room=room)
        logger.debug(f"Broadcast task update for task {task_id} to room {room}")
    
    async def broadcast_task_progress(self, instance_id: str, task_id: str, 
                                    progress: int, message: Optional[str] = None):
        """Broadcast task progress update."""
        update_data = {
            'progress': progress,
            'message': message,
            'timestamp': 'now'  # Add proper timestamp
        }
        
        await self.broadcast_task_update(instance_id, task_id, update_data)
    
    async def broadcast_task_status(self, instance_id: str, task_id: str, 
                                  status: str, error_message: Optional[str] = None):
        """Broadcast task status change."""
        update_data = {
            'status': status,
            'error_message': error_message,
            'timestamp': 'now'  # Add proper timestamp
        }
        
        await self.broadcast_task_update(instance_id, task_id, update_data)
    
    async def broadcast_execution_step(self, instance_id: str, task_id: str, 
                                     step: Dict[str, Any]):
        """Broadcast new execution step."""
        room = f"instance_{instance_id}"
        
        event_data = {
            'instance_id': instance_id,
            'task_id': task_id,
            'type': 'execution_step',
            'data': step
        }
        
        await self.sio.emit('execution_step', event_data, room=room)
        logger.debug(f"Broadcast execution step for task {task_id}")
    
    def get_connected_clients(self, instance_id: str) -> int:
        """Get count of connected clients for an instance."""
        return len(connected_clients.get(instance_id, set()))


# Global WebSocket manager instance
ws_manager = WebSocketManager(sio)