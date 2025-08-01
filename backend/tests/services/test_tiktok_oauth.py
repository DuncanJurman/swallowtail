"""Test TikTok OAuth service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.tiktok.oauth import TikTokOAuthService
from src.services.tiktok.models import TikTokTokenResponse, TikTokUserInfo


@pytest.mark.asyncio
async def test_generate_auth_url():
    """Test generating TikTok authorization URL."""
    instance_id = str(uuid4())
    scopes = ['user.info.basic', 'video.publish']
    
    async with TikTokOAuthService() as service:
        auth_url, state = await service.generate_auth_url(
            instance_id=instance_id,
            scopes=scopes
        )
        
        # Check auth URL contains required parameters
        assert 'https://www.tiktok.com/v2/auth/authorize' in auth_url
        assert 'client_key=' in auth_url
        assert 'response_type=code' in auth_url
        assert 'scope=user.info.basic%2Cvideo.publish' in auth_url
        assert 'redirect_uri=' in auth_url
        assert f'state={state}' in auth_url
        
        # State should be a valid hash
        assert len(state) == 64  # SHA256 hex digest length
        

@pytest.mark.asyncio
async def test_exchange_code_for_token():
    """Test exchanging authorization code for access token."""
    mock_response = {
        "access_token": "test_access_token",
        "expires_in": 86400,
        "open_id": "test_open_id",
        "refresh_expires_in": 31536000,
        "refresh_token": "test_refresh_token",
        "scope": "user.info.basic,video.publish",
        "token_type": "Bearer"
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=MagicMock(return_value=mock_response),
            raise_for_status=MagicMock()
        )
        
        async with TikTokOAuthService() as service:
            token_response = await service.exchange_code_for_token("test_code")
            
            assert isinstance(token_response, TikTokTokenResponse)
            assert token_response.access_token == "test_access_token"
            assert token_response.open_id == "test_open_id"
            assert token_response.token_type == "Bearer"
            
            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]['data']['code'] == "test_code"
            assert call_args[1]['data']['grant_type'] == "authorization_code"


@pytest.mark.asyncio
async def test_refresh_access_token():
    """Test refreshing access token."""
    mock_response = {
        "access_token": "new_access_token",
        "expires_in": 86400,
        "open_id": "test_open_id",
        "refresh_expires_in": 31536000,
        "refresh_token": "new_refresh_token",
        "scope": "user.info.basic,video.publish",
        "token_type": "Bearer"
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=MagicMock(return_value=mock_response),
            raise_for_status=MagicMock()
        )
        
        async with TikTokOAuthService() as service:
            token_response = await service.refresh_access_token("old_refresh_token")
            
            assert token_response.access_token == "new_access_token"
            assert token_response.refresh_token == "new_refresh_token"
            
            # Verify the request
            call_args = mock_post.call_args
            assert call_args[1]['data']['refresh_token'] == "old_refresh_token"
            assert call_args[1]['data']['grant_type'] == "refresh_token"


@pytest.mark.asyncio
async def test_get_user_info():
    """Test fetching TikTok user information."""
    mock_response = {
        "data": {
            "user": {
                "open_id": "test_open_id",
                "display_name": "Test User",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio_description": "Test bio",
                "is_verified": True,
                "follower_count": 1000,
                "following_count": 500,
                "likes_count": 5000,
                "video_count": 50
            }
        },
        "error": {
            "code": "ok",
            "message": ""
        }
    }
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=MagicMock(return_value=mock_response),
            raise_for_status=MagicMock()
        )
        
        async with TikTokOAuthService() as service:
            user_info = await service.get_user_info("test_access_token")
            
            assert isinstance(user_info, TikTokUserInfo)
            assert user_info.open_id == "test_open_id"
            assert user_info.display_name == "Test User"
            assert user_info.is_verified is True
            assert user_info.follower_count == 1000
            
            # Verify the request headers
            call_args = mock_get.call_args
            assert call_args[1]['headers']['Authorization'] == "Bearer test_access_token"


@pytest.mark.asyncio
async def test_verify_state():
    """Test CSRF state verification."""
    async with TikTokOAuthService() as service:
        # Test matching states
        assert service.verify_state("abc123", "abc123") is True
        
        # Test non-matching states
        assert service.verify_state("abc123", "xyz789") is False


@pytest.mark.asyncio
async def test_revoke_access():
    """Test revoking access token."""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            raise_for_status=MagicMock()
        )
        
        async with TikTokOAuthService() as service:
            result = await service.revoke_access("test_access_token")
            
            assert result is True
            
            # Verify the request
            call_args = mock_post.call_args
            assert call_args[1]['data']['token'] == "test_access_token"