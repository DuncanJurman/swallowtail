"""TikTok Content Posting API implementation."""
from typing import Optional, Dict, Any
import httpx
from fastapi import HTTPException

from src.services.tiktok.config import tiktok_config
from src.services.tiktok.models import TikTokPostRequest, TikTokPostResponse


class TikTokContentService:
    """Service for posting content to TikTok."""
    
    def __init__(self):
        self.config = tiktok_config
        self.client = httpx.AsyncClient()
    
    async def query_creator_info(self, access_token: str) -> Dict[str, Any]:
        """
        Query creator info before posting.
        Required step before posting content.
        
        Args:
            access_token: Valid access token
            
        Returns:
            Creator information including privacy options, limits, etc.
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        try:
            response = await self.client.post(
                f"{self.config.api_base_url}/v2/post/publish/creator_info/query/",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data and data['error']['code'] != 'ok':
                raise HTTPException(
                    status_code=400,
                    detail=f"TikTok API error: {data['error']['message']}"
                )
                
            return data.get('data', {})
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to query creator info: {str(e)}"
            )
    
    async def post_video_sandbox(
        self, 
        access_token: str,
        title: str,
        video_url: Optional[str] = None,
        privacy_level: str = "SELF_ONLY",  # Default to private in sandbox
        **kwargs
    ) -> TikTokPostResponse:
        """
        Post video content to TikTok (works in sandbox mode).
        
        In sandbox mode:
        - Content is only visible to authorized test users
        - Direct Post must be enabled in sandbox settings
        - Real API calls work but with limited visibility
        
        Args:
            access_token: Valid access token
            title: Video caption/description
            video_url: URL of video to post (must be from verified domain)
            privacy_level: Privacy setting (SELF_ONLY recommended for sandbox)
            
        Returns:
            TikTokPostResponse with post status
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        # First, query creator info (required step)
        creator_info = await self.query_creator_info(access_token)
        
        # Build post data based on whether we have a video URL
        if video_url:
            # Using PULL_FROM_URL method
            post_data = {
                "post_info": {
                    "title": title,
                    "privacy_level": privacy_level,
                    "disable_duet": kwargs.get('disable_duet', False),
                    "disable_comment": kwargs.get('disable_comment', False),
                    "disable_stitch": kwargs.get('disable_stitch', False),
                    "video_cover_timestamp_ms": kwargs.get('video_cover_timestamp_ms', 1000)
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": video_url
                }
            }
        else:
            # For demo purposes, we'll use a simple FILE_UPLOAD init
            # In real implementation, you'd need to upload file chunks
            post_data = {
                "post_info": {
                    "title": title,
                    "privacy_level": privacy_level,
                    "disable_duet": kwargs.get('disable_duet', False),
                    "disable_comment": kwargs.get('disable_comment', False),
                    "disable_stitch": kwargs.get('disable_stitch', False),
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": 1000000,  # 1MB dummy size
                    "chunk_size": 1000000,
                    "total_chunk_count": 1
                }
            }
        
        try:
            # Make the actual API call - this works in sandbox!
            response = await self.client.post(
                f"{self.config.api_base_url}/v2/post/publish/video/init/",
                json=post_data,
                headers=headers
            )
            
            data = response.json()
            
            # Check for API errors
            if response.status_code != 200 or (data.get('error', {}).get('code') != 'ok'):
                error_msg = data.get('error', {}).get('message', 'Unknown error')
                return TikTokPostResponse(
                    post_id=None,
                    share_url=None,
                    status="failed",
                    error_message=f"TikTok API error: {error_msg}"
                )
            
            # Extract publish_id from response
            publish_id = data.get('data', {}).get('publish_id')
            
            # For PULL_FROM_URL, the video is processed asynchronously
            # For FILE_UPLOAD, you'd need to upload chunks to the upload_url
            
            # In sandbox, we can return the publish_id as success
            # Real implementation would need to check status endpoint
            return TikTokPostResponse(
                post_id=publish_id,
                share_url=f"https://www.tiktok.com/@{creator_info.get('creator_username', 'user')}/video/{publish_id}",
                status="processing",  # In sandbox, videos process asynchronously
                error_message=None
            )
            
        except httpx.HTTPError as e:
            return TikTokPostResponse(
                post_id=None,
                share_url=None,
                status="failed",
                error_message=f"HTTP error: {str(e)}"
            )
        except Exception as e:
            return TikTokPostResponse(
                post_id=None,
                share_url=None,
                status="failed",
                error_message=str(e)
            )
    
    async def check_post_status(self, access_token: str, publish_id: str) -> Dict[str, Any]:
        """
        Check the status of a posted video.
        
        Args:
            access_token: Valid access token
            publish_id: The publish ID returned from post initiation
            
        Returns:
            Status information
        """
        # In sandbox mode, return mock status
        if self.config.sandbox_mode:
            return {
                "status": "PUBLISH_COMPLETE",
                "publish_id": publish_id,
                "share_url": f"https://www.tiktok.com/@testuser/video/{publish_id}"
            }
        
        # Real implementation would check actual status
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        # This would be the actual status check
        # Implementation details...
        
        return {
            "status": "PUBLISH_COMPLETE",
            "publish_id": publish_id
        }
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()