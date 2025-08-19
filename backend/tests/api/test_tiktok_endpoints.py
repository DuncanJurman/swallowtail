"""Test TikTok API endpoints with proper mocking."""

import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from src.models.instance import InstanceTaskStatus, TaskPriority
from src.models.instance_schemas import TikTokPostRequest, TikTokPostResponse
from src.api.routes.tasks import (
    post_task_to_tiktok,
    get_tiktok_post_status,
    get_task_detail
)


class TestTikTokEndpoints:
    """Test TikTok endpoints with comprehensive mocking."""
    
    @pytest.mark.asyncio
    async def test_post_to_tiktok_validates_task_status(self):
        """Test that posting validates task must be completed."""
        mock_db = Mock()
        mock_user_id = uuid4()
        task_id = uuid4()
        
        # Create a mock task that's not completed
        mock_task = Mock()
        mock_task.id = task_id
        mock_task.status = InstanceTaskStatus.IN_PROGRESS
        mock_task.can_post_to_tiktok = Mock(return_value=False)
        mock_task.get_video_url = Mock(return_value=None)
        
        # Setup query chain
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task
        
        post_request = TikTokPostRequest(
            title="Test post",
            privacy_level="SELF_ONLY"
        )
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id):
            response = await post_task_to_tiktok(
                task_id=task_id,
                post_request=post_request,
                db=mock_db,
                user_id=mock_user_id
            )
        
        assert response.success is False
        assert "must be completed" in response.message.lower()
        assert response.status == "FAILED"
    
    @pytest.mark.asyncio
    async def test_post_to_tiktok_validates_video_url(self):
        """Test that posting validates video URL from approved domains."""
        mock_db = Mock()
        mock_user_id = uuid4()
        task_id = uuid4()
        
        # Create a mock task with completed status but no video
        mock_task = Mock()
        mock_task.id = task_id
        mock_task.instance_id = uuid4()
        mock_task.status = InstanceTaskStatus.COMPLETED
        mock_task.can_post_to_tiktok = Mock(return_value=False)
        mock_task.get_video_url = Mock(return_value=None)
        mock_task.tiktok_post_status = None
        
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task
        
        post_request = TikTokPostRequest(
            title="Test post",
            privacy_level="SELF_ONLY"
        )
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id):
            response = await post_task_to_tiktok(
                task_id=task_id,
                post_request=post_request,
                db=mock_db,
                user_id=mock_user_id
            )
        
        assert response.success is False
        assert "no video output" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_post_to_tiktok_refreshes_expired_token(self):
        """Test that expired tokens are automatically refreshed."""
        mock_db = Mock()
        mock_user_id = uuid4()
        task_id = uuid4()
        instance_id = uuid4()
        
        # Create mock task
        mock_task = Mock()
        mock_task.id = task_id
        mock_task.instance_id = instance_id
        mock_task.status = InstanceTaskStatus.COMPLETED
        mock_task.can_post_to_tiktok = Mock(return_value=True)
        mock_task.get_video_url = Mock(return_value="https://test.supabase.co/storage/v1/videos/test.mp4")
        mock_task.update_tiktok_status = Mock()
        mock_task.tiktok_post_data = None
        
        # Create mock credentials with expired token
        mock_credentials = Mock()
        mock_credentials.id = uuid4()
        mock_credentials.instance_id = instance_id
        mock_credentials.is_expired = Mock(return_value=True)
        mock_credentials.get_access_token = Mock(return_value="old_token")
        mock_credentials.get_refresh_token = Mock(return_value="refresh_token")
        mock_credentials.access_token_encrypted = b"old"
        mock_credentials.refresh_token_encrypted = b"refresh"
        mock_credentials.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        
        # Setup database mocks - handle different query chains
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.first.return_value = mock_task
        mock_query.filter.return_value.filter.return_value.first.return_value = mock_credentials
        mock_query.filter.return_value.first.return_value = mock_credentials
        mock_db.query.return_value = mock_query
        
        post_request = TikTokPostRequest(
            title="Test with token refresh",
            privacy_level="SELF_ONLY"
        )
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id), \
             patch('src.services.tiktok.oauth.TikTokOAuthService') as MockOAuth, \
             patch('src.services.tiktok.content_api.TikTokContentAPI') as MockAPI:
            
            # Mock token refresh
            mock_oauth = MockOAuth.return_value
            mock_oauth.refresh_access_token = AsyncMock(return_value={
                "access_token": "new_token",
                "expires_in": 86400,
                "refresh_token": "new_refresh_token",
                "refresh_expires_in": 2592000
            })
            
            # Mock content API
            mock_api = MockAPI.return_value
            mock_api.query_creator_info = AsyncMock(return_value={
                "privacy_level_options": ["SELF_ONLY", "PUBLIC_TO_EVERYONE"]
            })
            mock_api.post_video_sandbox = AsyncMock(return_value={
                "publish_id": "v_pub_123456"
            })
            
            response = await post_task_to_tiktok(
                task_id=task_id,
                post_request=post_request,
                db=mock_db,
                user_id=mock_user_id
            )
        
        # Verify token was refreshed
        mock_oauth.refresh_access_token.assert_called_once_with("refresh_token")
        
        # Verify posting succeeded
        assert response.success is True
        assert response.publish_id == "v_pub_123456"
        assert response.status == "PROCESSING"
        
        # Verify task was updated
        mock_task.update_tiktok_status.assert_called_with(
            status="PROCESSING",
            publish_id="v_pub_123456"
        )
    
    @pytest.mark.asyncio
    async def test_check_post_status_updates_on_completion(self):
        """Test that checking status updates task when post completes."""
        mock_db = Mock()
        mock_user_id = uuid4()
        task_id = uuid4()
        
        # Create mock task with publish in progress
        mock_task = Mock()
        mock_task.id = task_id
        mock_task.instance_id = uuid4()
        mock_task.tiktok_publish_id = "v_pub_123456"
        mock_task.tiktok_post_status = "PROCESSING"
        mock_task.tiktok_post_url = None
        mock_task.tiktok_post_data = {
            "request": {"account_id": str(uuid4())}
        }
        mock_task.update_tiktok_status = Mock()
        
        # Create mock credentials
        mock_credentials = Mock()
        mock_credentials.get_access_token = Mock(return_value="token")
        mock_credentials.tiktok_open_id = "open_id"
        mock_credentials.display_name = "testuser"
        
        # Setup database mocks - handle different query chains
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.first.return_value = mock_task
        mock_query.filter.return_value.filter.return_value.first.return_value = mock_credentials
        mock_query.filter.return_value.first.return_value = mock_credentials
        mock_db.query.return_value = mock_query
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id), \
             patch('src.services.tiktok.content_api.TikTokContentAPI') as MockAPI:
            
            mock_api = MockAPI.return_value
            mock_api.check_post_status = AsyncMock(return_value={
                "status": "PUBLISH_COMPLETE",
                "publicaly_available_post_id": ["7123456789"],
                "uploaded_bytes": 1000000
            })
            
            response = await get_tiktok_post_status(
                task_id=task_id,
                db=mock_db,
                user_id=mock_user_id
            )
        
        assert response.status == "PUBLISH_COMPLETE"
        assert response.post_id == "7123456789"
        
        # Verify task was updated with published status
        mock_task.update_tiktok_status.assert_called_with(
            status="PUBLISHED",
            post_url="https://www.tiktok.com/@testuser/video/7123456789"
        )
        mock_db.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_check_post_status_handles_failure(self):
        """Test that checking status properly handles failed posts."""
        mock_db = Mock()
        mock_user_id = uuid4()
        task_id = uuid4()
        
        # Create mock task
        mock_task = Mock()
        mock_task.id = task_id
        mock_task.instance_id = uuid4()
        mock_task.tiktok_publish_id = "v_pub_failed"
        mock_task.tiktok_post_status = "PROCESSING"
        mock_task.tiktok_post_data = {"request": {"account_id": str(uuid4())}}
        mock_task.tiktok_post_url = None
        mock_task.update_tiktok_status = Mock()
        
        # Create mock credentials
        mock_credentials = Mock()
        mock_credentials.get_access_token = Mock(return_value="token")
        mock_credentials.tiktok_open_id = "open_id"
        mock_credentials.display_name = "testuser"
        
        # Setup database mocks - handle different query chains
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.first.return_value = mock_task
        mock_query.filter.return_value.filter.return_value.first.return_value = mock_credentials
        mock_query.filter.return_value.first.return_value = mock_credentials
        mock_db.query.return_value = mock_query
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id), \
             patch('src.services.tiktok.content_api.TikTokContentAPI') as MockAPI:
            
            mock_api = MockAPI.return_value
            mock_api.check_post_status = AsyncMock(return_value={
                "status": "FAILED",
                "fail_reason": "video_format_not_supported"
            })
            
            response = await get_tiktok_post_status(
                task_id=task_id,
                db=mock_db,
                user_id=mock_user_id
            )
        
        assert response.status == "FAILED"
        assert response.fail_reason == "video_format_not_supported"
        
        # Verify task was updated with failed status
        mock_task.update_tiktok_status.assert_called_with(
            status="FAILED",
            error="video_format_not_supported"
        )
    
    def test_task_detail_formats_execution_logs(self):
        """Test that task detail properly formats execution steps as logs."""
        mock_db = Mock()
        mock_user_id = uuid4()
        task_id = uuid4()
        
        # Create mock task with execution steps
        mock_task = Mock()
        mock_task.id = task_id
        mock_task.instance_id = uuid4()
        mock_task.description = "Create TikTok video for product"
        mock_task.status = InstanceTaskStatus.COMPLETED
        mock_task.priority = TaskPriority.NORMAL
        mock_task.output_format = "video"
        mock_task.output_data = {
            "video_url": "https://test.supabase.co/storage/v1/videos/test.mp4",
            "caption": "Check out this product!"
        }
        mock_task.execution_steps = [
            {
                "step_id": "1",
                "agent": "TrendAnalyzer",
                "action": "Analyzed trends",
                "status": "success",
                "output": {"message": "Found trending audio"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "step_id": "2",
                "agent": "VideoGenerator",
                "action": "Generated video",
                "status": "success",
                "output": {"message": "Video created successfully"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
        mock_task.attached_media_ids = []
        mock_task.error_message = None
        mock_task.tiktok_post_data = None
        mock_task.tiktok_publish_id = None
        mock_task.tiktok_post_status = None
        mock_task.tiktok_post_url = None
        mock_task.scheduled_post_time = None
        mock_task.created_at = datetime.now(timezone.utc)
        mock_task.updated_at = datetime.now(timezone.utc)
        mock_task.processing_started_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        mock_task.processing_ended_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        mock_task.can_post_to_tiktok = Mock(return_value=True)
        mock_task.output_media_ids = []
        
        # Setup database mocks
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id):
            response = get_task_detail(
                task_id=task_id,
                db=mock_db,
                user_id=mock_user_id
            )
        
        # Verify execution logs were created
        assert len(response.execution_logs) == 2
        assert response.execution_logs[0].agent_name == "TrendAnalyzer"
        assert response.execution_logs[1].agent_name == "VideoGenerator"
        
        # Verify planning steps were generated
        assert len(response.planning) > 0
        
        # Verify TikTok readiness
        assert response.can_post_to_tiktok is True
        assert response.suggested_caption == "Check out this product!"
    
    @pytest.mark.asyncio
    async def test_posting_prevents_duplicate_posts(self):
        """Test that tasks already being posted can't be posted again."""
        mock_db = Mock()
        mock_user_id = uuid4()
        task_id = uuid4()
        
        # Create task that's already posting
        mock_task = Mock()
        mock_task.id = task_id
        mock_task.status = InstanceTaskStatus.COMPLETED
        mock_task.tiktok_post_status = "PROCESSING"
        mock_task.can_post_to_tiktok = Mock(return_value=False)
        mock_task.get_video_url = Mock(return_value="https://test.supabase.co/storage/v1/videos/test.mp4")
        
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task
        
        post_request = TikTokPostRequest(
            title="Duplicate post attempt",
            privacy_level="SELF_ONLY"
        )
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id):
            response = await post_task_to_tiktok(
                task_id=task_id,
                post_request=post_request,
                db=mock_db,
                user_id=mock_user_id
            )
        
        assert response.success is False
        assert "already posted or posting" in response.message.lower()