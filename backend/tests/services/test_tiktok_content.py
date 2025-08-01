"""Test TikTok Content API service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.tiktok.content_api import TikTokContentService
from src.services.tiktok.models import TikTokPostResponse


@pytest.mark.asyncio
async def test_query_creator_info():
    """Test querying creator information."""
    mock_response = {
        "data": {
            "creator_avatar_url": "https://example.com/avatar.jpg",
            "creator_username": "testuser",
            "creator_nickname": "Test User",
            "privacy_level_options": ["PUBLIC_TO_EVERYONE", "SELF_ONLY"],
            "comment_disabled": False,
            "duet_disabled": False,
            "stitch_disabled": True,
            "max_video_post_duration_sec": 300
        },
        "error": {
            "code": "ok",
            "message": ""
        }
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=MagicMock(return_value=mock_response),
            raise_for_status=MagicMock()
        )
        
        async with TikTokContentService() as service:
            creator_info = await service.query_creator_info("test_access_token")
            
            assert creator_info["creator_username"] == "testuser"
            assert creator_info["max_video_post_duration_sec"] == 300
            assert "PUBLIC_TO_EVERYONE" in creator_info["privacy_level_options"]
            
            # Verify the request headers
            call_args = mock_post.call_args
            assert call_args[1]['headers']['Authorization'] == "Bearer test_access_token"


@pytest.mark.asyncio
async def test_post_video_sandbox_with_url():
    """Test posting video using PULL_FROM_URL method."""
    # Mock creator info response
    mock_creator_response = {
        "data": {
            "creator_username": "testuser",
            "privacy_level_options": ["PUBLIC_TO_EVERYONE", "SELF_ONLY"]
        },
        "error": {"code": "ok", "message": ""}
    }
    
    # Mock post init response
    mock_post_response = {
        "data": {
            "publish_id": "v_pub_url~v2.123456789"
        },
        "error": {"code": "ok", "message": ""}
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        # Set up different responses for different calls
        mock_post.side_effect = [
            AsyncMock(
                status_code=200,
                json=MagicMock(return_value=mock_creator_response),
                raise_for_status=MagicMock()
            ),
            AsyncMock(
                status_code=200,
                json=MagicMock(return_value=mock_post_response),
                raise_for_status=MagicMock()
            )
        ]
        
        async with TikTokContentService() as service:
            response = await service.post_video_sandbox(
                access_token="test_access_token",
                title="Test video #tiktok",
                video_url="https://example.com/video.mp4",
                privacy_level="SELF_ONLY"
            )
            
            assert isinstance(response, TikTokPostResponse)
            assert response.post_id == "v_pub_url~v2.123456789"
            assert response.status == "processing"
            assert response.share_url is not None
            
            # Verify two calls were made
            assert mock_post.call_count == 2
            
            # Check the post init request
            post_call = mock_post.call_args_list[1]
            post_data = post_call[1]['json']
            assert post_data['post_info']['title'] == "Test video #tiktok"
            assert post_data['post_info']['privacy_level'] == "SELF_ONLY"
            assert post_data['source_info']['source'] == "PULL_FROM_URL"
            assert post_data['source_info']['video_url'] == "https://example.com/video.mp4"


@pytest.mark.asyncio
async def test_post_video_sandbox_file_upload():
    """Test posting video using FILE_UPLOAD method."""
    mock_creator_response = {
        "data": {"creator_username": "testuser"},
        "error": {"code": "ok", "message": ""}
    }
    
    mock_post_response = {
        "data": {"publish_id": "v_pub_file~v2.123456789"},
        "error": {"code": "ok", "message": ""}
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = [
            AsyncMock(
                status_code=200,
                json=MagicMock(return_value=mock_creator_response),
                raise_for_status=MagicMock()
            ),
            AsyncMock(
                status_code=200,
                json=MagicMock(return_value=mock_post_response),
                raise_for_status=MagicMock()
            )
        ]
        
        async with TikTokContentService() as service:
            response = await service.post_video_sandbox(
                access_token="test_access_token",
                title="Test video",
                video_url=None  # No URL means FILE_UPLOAD
            )
            
            assert response.post_id == "v_pub_file~v2.123456789"
            assert response.status == "processing"
            
            # Check the request used FILE_UPLOAD
            post_call = mock_post.call_args_list[1]
            post_data = post_call[1]['json']
            assert post_data['source_info']['source'] == "FILE_UPLOAD"
            assert 'video_size' in post_data['source_info']


@pytest.mark.asyncio
async def test_post_video_api_error():
    """Test handling API error during video post."""
    mock_creator_response = {
        "data": {"creator_username": "testuser"},
        "error": {"code": "ok", "message": ""}
    }
    
    mock_error_response = {
        "error": {
            "code": "invalid_param",
            "message": "Invalid privacy level"
        }
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = [
            AsyncMock(
                status_code=200,
                json=MagicMock(return_value=mock_creator_response),
                raise_for_status=MagicMock()
            ),
            AsyncMock(
                status_code=400,
                json=MagicMock(return_value=mock_error_response),
                raise_for_status=MagicMock()
            )
        ]
        
        async with TikTokContentService() as service:
            response = await service.post_video_sandbox(
                access_token="test_access_token",
                title="Test video",
                privacy_level="INVALID_LEVEL"
            )
            
            assert response.status == "failed"
            assert response.post_id is None
            assert "Invalid privacy level" in response.error_message


@pytest.mark.asyncio
async def test_check_post_status_sandbox():
    """Test checking post status in sandbox mode."""
    async with TikTokContentService() as service:
        # In sandbox mode, it returns mock status
        status = await service.check_post_status(
            access_token="test_access_token",
            publish_id="v_pub_url~v2.123456789"
        )
        
        assert status["status"] == "PUBLISH_COMPLETE"
        assert status["publish_id"] == "v_pub_url~v2.123456789"
        assert "share_url" in status