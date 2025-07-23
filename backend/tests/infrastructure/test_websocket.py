"""Tests for WebSocket functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from src.core.websocket import WebSocketManager, connected_clients


class TestWebSocketManager:
    """Test cases for WebSocketManager."""
    
    @pytest.fixture
    def mock_sio(self):
        """Create a mock Socket.io server."""
        sio = AsyncMock()
        sio.emit = AsyncMock()
        sio.enter_room = AsyncMock()
        sio.leave_room = AsyncMock()
        sio.save_session = AsyncMock()
        return sio
    
    @pytest.fixture
    def ws_manager(self, mock_sio):
        """Create WebSocketManager with mock server."""
        return WebSocketManager(mock_sio)
    
    @pytest.mark.asyncio
    async def test_broadcast_task_update(self, ws_manager, mock_sio):
        """Test broadcasting task update."""
        instance_id = str(uuid4())
        task_id = str(uuid4())
        update_data = {"status": "completed"}
        
        await ws_manager.broadcast_task_update(instance_id, task_id, update_data)
        
        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == 'task_update'
        assert call_args[0][1]['instance_id'] == instance_id
        assert call_args[0][1]['task_id'] == task_id
        assert call_args[0][1]['data'] == update_data
        assert call_args[1]['room'] == f"instance_{instance_id}"
    
    @pytest.mark.asyncio
    async def test_broadcast_task_progress(self, ws_manager, mock_sio):
        """Test broadcasting task progress."""
        instance_id = str(uuid4())
        task_id = str(uuid4())
        progress = 75
        message = "Processing data..."
        
        await ws_manager.broadcast_task_progress(instance_id, task_id, progress, message)
        
        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        event_data = call_args[0][1]
        assert event_data['data']['progress'] == progress
        assert event_data['data']['message'] == message
    
    @pytest.mark.asyncio
    async def test_broadcast_task_status(self, ws_manager, mock_sio):
        """Test broadcasting task status change."""
        instance_id = str(uuid4())
        task_id = str(uuid4())
        status = "failed"
        error_message = "API error"
        
        await ws_manager.broadcast_task_status(instance_id, task_id, status, error_message)
        
        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        event_data = call_args[0][1]
        assert event_data['data']['status'] == status
        assert event_data['data']['error_message'] == error_message
    
    @pytest.mark.asyncio
    async def test_broadcast_execution_step(self, ws_manager, mock_sio):
        """Test broadcasting execution step."""
        instance_id = str(uuid4())
        task_id = str(uuid4())
        step = {
            "step_id": "step_1",
            "agent": "ContentCreator",
            "action": "Generating content",
            "status": "completed"
        }
        
        await ws_manager.broadcast_execution_step(instance_id, task_id, step)
        
        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == 'execution_step'
        assert call_args[0][1]['data'] == step
    
    def test_get_connected_clients(self, ws_manager):
        """Test getting connected client count."""
        instance_id = "test-instance"
        
        # No clients connected
        assert ws_manager.get_connected_clients(instance_id) == 0
        
        # Add some clients
        connected_clients[instance_id] = {"client1", "client2", "client3"}
        assert ws_manager.get_connected_clients(instance_id) == 3
        
        # Clean up
        del connected_clients[instance_id]


class TestWebSocketHandlers:
    """Test Socket.io event handlers."""
    
    @pytest.fixture
    def setup_handlers(self):
        """Set up handlers for testing."""
        # Import to register handlers
        from src.core.websocket import ws_manager
        return ws_manager
    
    @pytest.mark.asyncio
    async def test_connection_handler(self, setup_handlers):
        """Test client connection handling."""
        # This would require more complex Socket.io test client setup
        # For now, we're testing the manager methods directly
        pass
    
    @pytest.mark.asyncio
    async def test_subscribe_instance_handler(self, setup_handlers):
        """Test instance subscription handling."""
        # This would require Socket.io test client
        pass