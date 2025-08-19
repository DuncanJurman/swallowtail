"""Integration tests for TikTok content posting flow."""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock, Mock

from src.models.instance import (
    Instance, 
    InstanceTask, 
    InstanceTaskStatus,
    TaskPriority,
    InstanceType
)
from src.models.tiktok_credentials import InstanceTikTokCredentials
from src.models.instance_schemas import (
    TikTokPostRequest,
    TaskDetailResponse
)


class TestTikTokPostingFlow:
    """Test the complete TikTok posting workflow using mocked dependencies."""
    
    @pytest.fixture
    def mock_user_id(self):
        """Mock user ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = Mock()
        session.query = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.refresh = Mock()
        return session
    
    @pytest.fixture
    def mock_instance(self, mock_user_id):
        """Create a test instance."""
        instance = Instance(
            id=uuid4(),
            user_id=mock_user_id,
            name="Test Instance",
            type=InstanceType.SOCIAL_MEDIA,
            business_profile={"name": "Test Business"},
            configuration={}
        )
        return instance
    
    @pytest.fixture
    def mock_task_with_video(self, mock_instance):
        """Create a test task with video output."""
        task = Mock(spec=InstanceTask)
        task.id = uuid4()
        task.instance_id = mock_instance.id
        task.description = "Create a TikTok video about our product"
        task.status = InstanceTaskStatus.COMPLETED
        task.priority = TaskPriority.NORMAL
        task.output_format = "video"
        task.output_data = {
            "video_url": "https://test.supabase.co/storage/v1/videos/test.mp4",
            "caption": "Check out our amazing product! #product #demo",
            "duration": 30
        }
        task.execution_steps = [
            {
                "step_id": "1",
                "agent": "ContentCreator",
                "action": "Generate video",
                "status": "completed",
                "output": {"message": "Video generated successfully"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
        task.created_at = datetime.now(timezone.utc)
        task.updated_at = datetime.now(timezone.utc)
        task.processing_started_at = None
        task.processing_ended_at = None
        task.attached_media_ids = []
        task.error_message = None
        task.tiktok_post_data = None
        task.tiktok_publish_id = None
        task.tiktok_post_status = None
        task.tiktok_post_url = None
        task.scheduled_post_time = None
        
        # Add helper methods
        task.can_post_to_tiktok = MagicMock(return_value=True)
        task.get_video_url = MagicMock(return_value="https://test.supabase.co/storage/v1/videos/test.mp4")
        task.update_tiktok_status = MagicMock()
        
        return task
    
    @pytest.fixture
    def mock_tiktok_credentials(self, mock_instance):
        """Create mock TikTok credentials."""
        credentials = Mock(spec=InstanceTikTokCredentials)
        credentials.id = uuid4()
        credentials.instance_id = mock_instance.id
        credentials.account_name = "Test Account"
        credentials.tiktok_open_id = "test_open_id"
        credentials.display_name = "testuser"
        credentials.avatar_url = "https://example.com/avatar.jpg"
        credentials.expires_at = datetime.now(timezone.utc).replace(hour=23, minute=59)
        credentials.scopes = "video.publish"
        
        # Mock the decryption methods
        credentials.get_access_token = MagicMock(return_value="test_access_token")
        credentials.get_refresh_token = MagicMock(return_value="test_refresh_token")
        credentials.is_expired = MagicMock(return_value=False)
        
        return credentials
    
    @pytest.mark.asyncio
    async def test_task_detail_with_video_output(
        self, 
        mock_db_session,
        mock_task_with_video,
        mock_user_id,
        mock_instance
    ):
        """Test that task detail endpoint properly formats video task data."""
        from src.api.routes.tasks import get_task_detail
        
        # Setup mock query results
        mock_db_session.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task_with_video
        mock_db_session.query.return_value.filter.return_value.all.return_value = []
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id), \
             patch('src.api.routes.tasks.get_db', return_value=mock_db_session):
            response = get_task_detail(
                task_id=mock_task_with_video.id,
                db=mock_db_session,
                user_id=mock_user_id
            )
        
        assert isinstance(response, TaskDetailResponse)
        assert response.id == mock_task_with_video.id
        assert response.status == InstanceTaskStatus.COMPLETED
        assert response.can_post_to_tiktok is True
        assert response.suggested_caption == "Check out our amazing product! #product #demo"
        assert len(response.planning) > 0
        assert len(response.execution_logs) > 0
        assert response.output_data["video_url"] == "https://test.supabase.co/storage/v1/videos/test.mp4"
    
    @pytest.mark.asyncio
    async def test_post_to_tiktok_success(
        self,
        mock_db_session,
        mock_task_with_video,
        mock_tiktok_credentials,
        mock_user_id
    ):
        """Test successful posting to TikTok."""
        from src.api.routes.tasks import post_task_to_tiktok
        
        post_request = TikTokPostRequest(
            title="Amazing product demo! #product #tiktok",
            privacy_level="SELF_ONLY",
            disable_duet=False,
            disable_stitch=False,
            disable_comment=False
        )
        
        # Setup mock database queries
        mock_db_session.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task_with_video
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_tiktok_credentials
        
        # Mock the TikTok API calls
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id), \
             patch('src.api.routes.tasks.get_db', return_value=mock_db_session), \
             patch('src.services.tiktok.content_api.TikTokContentAPI') as MockContentAPI:
            
            # Setup mock API
            mock_api = MockContentAPI.return_value
            mock_api.query_creator_info = AsyncMock(return_value={
                "creator_username": "testuser",
                "privacy_level_options": ["PUBLIC_TO_EVERYONE", "SELF_ONLY"],
                "max_video_post_duration_sec": 300
            })
            mock_api.post_video_sandbox = AsyncMock(return_value={
                "publish_id": "v_pub_123456"
            })
            
            response = await post_task_to_tiktok(
                task_id=mock_task_with_video.id,
                post_request=post_request,
                db=mock_db_session,
                user_id=mock_user_id
            )
        
        assert response.success is True
        assert response.publish_id == "v_pub_123456"
        assert response.status == "PROCESSING"
        assert response.task_id == mock_task_with_video.id
        
        # Verify task update methods were called
        mock_task_with_video.update_tiktok_status.assert_called_with(
            status="PROCESSING",
            publish_id="v_pub_123456"
        )
        assert mock_db_session.commit.called
    
    @pytest.mark.asyncio
    async def test_post_to_tiktok_no_video(
        self,
        mock_db_session,
        mock_instance,
        mock_user_id
    ):
        """Test posting fails when task has no video output."""
        from src.api.routes.tasks import post_task_to_tiktok
        
        # Create task without video
        task = Mock(spec=InstanceTask)
        task.id = uuid4()
        task.instance_id = mock_instance.id
        task.description = "Research task"
        task.status = InstanceTaskStatus.COMPLETED
        task.output_data = {"research": "Some findings"}
        task.can_post_to_tiktok = MagicMock(return_value=False)
        task.get_video_url = MagicMock(return_value=None)
        
        mock_db_session.query.return_value.join.return_value.filter.return_value.first.return_value = task
        
        post_request = TikTokPostRequest(
            title="Test post",
            privacy_level="SELF_ONLY"
        )
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id), \
             patch('src.api.routes.tasks.get_db', return_value=mock_db_session):
            response = await post_task_to_tiktok(
                task_id=task.id,
                post_request=post_request,
                db=mock_db_session,
                user_id=mock_user_id
            )
        
        assert response.success is False
        assert response.status == "FAILED"
        assert "no video output" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_post_to_tiktok_no_credentials(
        self,
        mock_db_session,
        mock_task_with_video,
        mock_user_id
    ):
        """Test posting fails when no TikTok account is connected."""
        from src.api.routes.tasks import post_task_to_tiktok
        
        post_request = TikTokPostRequest(
            title="Test post",
            privacy_level="SELF_ONLY"
        )
        
        # Setup mocks - no credentials found
        mock_db_session.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task_with_video
        mock_db_session.query.return_value.filter.return_value.first.return_value = None  # No credentials
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id), \
             patch('src.api.routes.tasks.get_db', return_value=mock_db_session):
            response = await post_task_to_tiktok(
                task_id=mock_task_with_video.id,
                post_request=post_request,
                db=mock_db_session,
                user_id=mock_user_id
            )
        
        assert response.success is False
        assert response.status == "FAILED"
        assert "no tiktok account connected" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_post_status_published(
        self,
        mock_db_session,
        mock_instance,
        mock_tiktok_credentials,
        mock_user_id
    ):
        """Test checking status of a published post."""
        from src.api.routes.tasks import get_tiktok_post_status
        
        # Create task with TikTok post in progress
        task = Mock(spec=InstanceTask)
        task.id = uuid4()
        task.instance_id = mock_instance.id
        task.description = "Posted video"
        task.status = InstanceTaskStatus.COMPLETED
        task.output_data = {"video_url": "https://test.supabase.co/storage/v1/videos/test.mp4"}
        task.tiktok_publish_id = "v_pub_123456"
        task.tiktok_post_status = "PROCESSING"
        task.tiktok_post_url = None
        task.tiktok_post_data = {
            "request": {
                "account_id": str(mock_tiktok_credentials.id)
            }
        }
        task.update_tiktok_status = MagicMock()
        
        # Setup mock queries
        mock_db_session.query.return_value.join.return_value.filter.return_value.first.return_value = task
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_tiktok_credentials
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id), \
             patch('src.api.routes.tasks.get_db', return_value=mock_db_session), \
             patch('src.services.tiktok.content_api.TikTokContentAPI') as MockContentAPI:
            
            # Mock successful publish
            mock_api = MockContentAPI.return_value
            mock_api.check_post_status = AsyncMock(return_value={
                "status": "PUBLISH_COMPLETE",
                "publicaly_available_post_id": ["7123456789"],
                "uploaded_bytes": 1000000
            })
            
            response = await get_tiktok_post_status(
                task_id=task.id,
                db=mock_db_session,
                user_id=mock_user_id
            )
        
        assert response.status == "PUBLISH_COMPLETE"
        assert response.publish_id == "v_pub_123456"
        assert response.post_id == "7123456789"
        
        # Verify task was updated
        task.update_tiktok_status.assert_called_with(
            status="PUBLISHED",
            post_url=f"https://www.tiktok.com/@{mock_tiktok_credentials.display_name}/video/7123456789"
        )
        assert mock_db_session.commit.called
    
    @pytest.mark.asyncio  
    async def test_check_post_status_failed(
        self,
        mock_db_session,
        mock_instance,
        mock_tiktok_credentials,
        mock_user_id
    ):
        """Test checking status of a failed post."""
        from src.api.routes.tasks import get_tiktok_post_status
        
        task = Mock(spec=InstanceTask)
        task.id = uuid4()
        task.instance_id = mock_instance.id
        task.description = "Failed video"
        task.status = InstanceTaskStatus.COMPLETED
        task.output_data = {"video_url": "https://test.supabase.co/storage/v1/videos/test.mp4"}
        task.tiktok_publish_id = "v_pub_failed"
        task.tiktok_post_status = "PROCESSING"
        task.tiktok_post_url = None
        task.tiktok_post_data = {
            "request": {
                "account_id": str(mock_tiktok_credentials.id)
            }
        }
        task.update_tiktok_status = MagicMock()
        
        # Setup mock queries
        mock_db_session.query.return_value.join.return_value.filter.return_value.first.return_value = task
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_tiktok_credentials
        
        with patch('src.api.routes.tasks.get_current_user_id', return_value=mock_user_id), \
             patch('src.api.routes.tasks.get_db', return_value=mock_db_session), \
             patch('src.services.tiktok.content_api.TikTokContentAPI') as MockContentAPI:
            
            # Mock failed publish
            mock_api = MockContentAPI.return_value
            mock_api.check_post_status = AsyncMock(return_value={
                "status": "FAILED",
                "fail_reason": "video_pull_failed"
            })
            
            response = await get_tiktok_post_status(
                task_id=task.id,
                db=mock_db_session,
                user_id=mock_user_id
            )
        
        assert response.status == "FAILED"
        assert response.fail_reason == "video_pull_failed"
        
        # Verify task was updated
        task.update_tiktok_status.assert_called_with(
            status="FAILED",
            error="video_pull_failed"
        )
        assert mock_db_session.commit.called