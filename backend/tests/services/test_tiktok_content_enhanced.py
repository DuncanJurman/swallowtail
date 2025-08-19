"""Tests for enhanced TikTok content service functionality."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
import httpx

from src.services.tiktok.content_api import TikTokContentAPI
from src.models.instance import InstanceTask, InstanceTaskStatus


class TestTikTokContentAPI:
    """Test the enhanced TikTok Content API."""
    
    @pytest.fixture
    def content_api(self):
        """Create a TikTok Content API instance."""
        return TikTokContentAPI(
            access_token="test_token",
            open_id="test_open_id"
        )
    
    @pytest.mark.asyncio
    async def test_query_creator_info_success(self, content_api):
        """Test successful creator info query."""
        mock_response_data = {
            "data": {
                "creator_username": "testuser",
                "creator_nickname": "Test User",
                "privacy_level_options": ["PUBLIC_TO_EVERYONE", "SELF_ONLY"],
                "max_video_post_duration_sec": 300,
                "comment_disabled": False,
                "duet_disabled": False,
                "stitch_disabled": False
            },
            "error": {"code": "ok", "message": ""}
        }
        
        with patch.object(content_api.client, 'post', new_callable=AsyncMock) as mock_post:
            # Create a proper mock response
            mock_resp = MagicMock()
            mock_resp.json = MagicMock(return_value=mock_response_data)
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp
            
            result = await content_api.query_creator_info()
        
        assert result["creator_username"] == "testuser"
        assert "PUBLIC_TO_EVERYONE" in result["privacy_level_options"]
        assert result["max_video_post_duration_sec"] == 300
    
    @pytest.mark.asyncio
    async def test_query_creator_info_with_retry(self, content_api):
        """Test creator info query with retry on rate limit."""
        mock_error_response = MagicMock()
        mock_error_response.status_code = 429
        
        mock_success_response = MagicMock()
        mock_success_response.json.return_value = {
            "data": {"creator_username": "testuser"},
            "error": {"code": "ok"}
        }
        mock_success_response.raise_for_status = MagicMock()
        
        with patch.object(content_api.client, 'post', new_callable=AsyncMock) as mock_post:
            # First call fails with rate limit, second succeeds
            mock_post.side_effect = [
                httpx.HTTPStatusError("Rate limited", request=None, response=mock_error_response),
                mock_success_response
            ]
            
            result = await content_api.query_creator_info()
        
        assert result["creator_username"] == "testuser"
        assert mock_post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_post_video_sandbox_success(self, content_api):
        """Test successful video posting."""
        mock_response_data = {
            "data": {
                "publish_id": "v_pub_123456",
                "upload_url": None  # PULL_FROM_URL doesn't return upload_url
            },
            "error": {"code": "ok", "message": ""}
        }
        
        with patch.object(content_api.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_resp = MagicMock()
            mock_resp.json = MagicMock(return_value=mock_response_data)
            mock_resp.status_code = 200
            mock_post.return_value = mock_resp
            
            result = await content_api.post_video_sandbox(
                video_url="https://test.supabase.co/storage/v1/videos/test.mp4",
                title="Test video #tiktok",
                privacy_level="SELF_ONLY",
                disable_duet=True,
                disable_comment=False
            )
        
        assert result["publish_id"] == "v_pub_123456"
        
        # Verify request payload
        call_args = mock_post.call_args
        request_data = call_args.kwargs["json"]
        assert request_data["post_info"]["title"] == "Test video #tiktok"
        assert request_data["post_info"]["privacy_level"] == "SELF_ONLY"
        assert request_data["post_info"]["disable_duet"] is True
        assert request_data["source_info"]["source"] == "PULL_FROM_URL"
    
    @pytest.mark.asyncio
    async def test_post_video_invalid_url(self, content_api):
        """Test posting with invalid video URL."""
        with pytest.raises(ValueError, match="Invalid video URL"):
            await content_api.post_video_sandbox(
                video_url="https://example.com/video.mp4",  # Not a verified domain
                title="Test video"
            )
    
    @pytest.mark.asyncio
    async def test_post_video_handles_api_errors(self, content_api):
        """Test proper error handling for TikTok API errors."""
        from fastapi import HTTPException
        
        mock_response_data = {
            "error": {
                "code": "spam_risk_too_many_posts",
                "message": "Daily post limit reached"
            }
        }
        
        with patch.object(content_api.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_resp = MagicMock()
            mock_resp.json = MagicMock(return_value=mock_response_data)
            mock_resp.status_code = 403
            mock_post.return_value = mock_resp
            
            with pytest.raises(HTTPException) as exc_info:
                await content_api.post_video_sandbox(
                    video_url="https://test.supabase.co/storage/v1/videos/test.mp4",
                    title="Test video"
                )
            
            assert exc_info.value.status_code == 429
            assert "Daily post limit reached" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_check_post_status_success(self, content_api):
        """Test checking post status."""
        mock_response_data = {
            "data": {
                "status": "PUBLISH_COMPLETE",
                "publicaly_available_post_id": ["7123456789"],
                "uploaded_bytes": 1000000
            },
            "error": {"code": "ok", "message": ""}
        }
        
        with patch.object(content_api.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_resp = MagicMock()
            mock_resp.json = MagicMock(return_value=mock_response_data)
            mock_post.return_value = mock_resp
            
            result = await content_api.check_post_status("v_pub_123456")
        
        assert result["status"] == "PUBLISH_COMPLETE"
        assert result["publicaly_available_post_id"] == ["7123456789"]
    
    @pytest.mark.asyncio
    async def test_post_video_from_task(self, content_api):
        """Test posting video from a task object."""
        # Create mock task
        task = MagicMock(spec=InstanceTask)
        task.get_video_url.return_value = "https://test.supabase.co/storage/v1/videos/task.mp4"
        task.output_data = {
            "caption": "Generated caption #ai #content",
            "video_url": "https://test.supabase.co/storage/v1/videos/task.mp4"
        }
        task.instance_id = uuid4()
        
        mock_response_data = {
            "data": {"publish_id": "v_pub_from_task"},
            "error": {"code": "ok"}
        }
        
        with patch.object(content_api.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_resp = MagicMock()
            mock_resp.json = MagicMock(return_value=mock_response_data)
            mock_resp.status_code = 200
            mock_post.return_value = mock_resp
            
            result = await content_api.post_video_from_task(
                task=task,
                privacy_level="PUBLIC_TO_EVERYONE"
            )
        
        assert result["publish_id"] == "v_pub_from_task"
        
        # Verify it used the task's caption
        call_args = mock_post.call_args
        request_data = call_args.kwargs["json"]
        assert request_data["post_info"]["title"] == "Generated caption #ai #content"
    
    @pytest.mark.asyncio
    async def test_post_video_from_task_no_video(self, content_api):
        """Test posting from task without video fails."""
        task = MagicMock(spec=InstanceTask)
        task.get_video_url.return_value = None
        
        with pytest.raises(ValueError, match="Task has no video output"):
            await content_api.post_video_from_task(task)
    
    @pytest.mark.asyncio
    async def test_cancel_post(self, content_api):
        """Test cancelling a post."""
        mock_response_data = {
            "error": {"code": "ok", "message": ""}
        }
        
        with patch.object(content_api.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_resp = MagicMock()
            mock_resp.json = MagicMock(return_value=mock_response_data)
            mock_post.return_value = mock_resp
            
            result = await content_api.cancel_post("v_pub_123456")
        
        assert result is True
    
    def test_validate_video_url(self, content_api):
        """Test URL validation for various domains."""
        # Valid URLs
        assert content_api._is_valid_video_url("https://test.supabase.co/storage/v1/videos/test.mp4")
        assert content_api._is_valid_video_url("https://project.supabase.io/storage/videos/test.mp4")
        assert content_api._is_valid_video_url("https://storage.googleapis.com/bucket/video.mp4")
        assert content_api._is_valid_video_url("https://s3.amazonaws.com/bucket/video.mp4")
        
        # Invalid URLs
        assert not content_api._is_valid_video_url("https://example.com/video.mp4")
        assert not content_api._is_valid_video_url("http://supabase.co/video.mp4")  # Not HTTPS
        assert not content_api._is_valid_video_url("not-a-url")
        assert not content_api._is_valid_video_url("")