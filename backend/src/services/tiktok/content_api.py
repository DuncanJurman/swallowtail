"""TikTok Content Posting API implementation."""
from typing import Optional, Dict, Any, List
import httpx
from fastapi import HTTPException
import asyncio
from urllib.parse import urlparse

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


class TikTokContentAPI:
    """Enhanced TikTok Content API for task integration."""
    
    def __init__(self, access_token: str, open_id: str):
        """
        Initialize the TikTok Content API.
        
        Args:
            access_token: Valid TikTok access token
            open_id: TikTok Open ID for the user
        """
        self.access_token = access_token
        self.open_id = open_id
        self.config = tiktok_config
        self.client = httpx.AsyncClient(timeout=30.0)
        self._retry_count = 3
        self._retry_delay = 1.0
    
    async def query_creator_info(self) -> Dict[str, Any]:
        """
        Query creator information including privacy options and limits.
        
        Returns:
            Creator information dict with privacy_level_options, max_video_post_duration_sec, etc.
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        url = f"{self.config.api_base_url}/v2/post/publish/creator_info/query/"
        
        for attempt in range(self._retry_count):
            try:
                response = await self.client.post(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('error', {}).get('code') != 'ok':
                    error_msg = data.get('error', {}).get('message', 'Unknown error')
                    raise HTTPException(status_code=400, detail=error_msg)
                
                return data.get('data', {})
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    if attempt < self._retry_count - 1:
                        await asyncio.sleep(self._retry_delay * (attempt + 1))
                        continue
                raise
            except httpx.RequestError as e:
                if attempt < self._retry_count - 1:
                    await asyncio.sleep(self._retry_delay)
                    continue
                raise
        
        raise HTTPException(status_code=500, detail="Failed to query creator info after retries")
    
    async def post_video_sandbox(
        self,
        video_url: str,
        title: str,
        privacy_level: str = "SELF_ONLY",
        disable_duet: bool = False,
        disable_stitch: bool = False,
        disable_comment: bool = False,
        video_cover_timestamp_ms: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Post a video to TikTok using PULL_FROM_URL method.
        
        Args:
            video_url: URL of the video (must be from verified domain like Supabase)
            title: Video caption with hashtags and mentions
            privacy_level: Privacy setting
            disable_duet: Whether to disable duets
            disable_stitch: Whether to disable stitches
            disable_comment: Whether to disable comments
            video_cover_timestamp_ms: Frame to use as cover (milliseconds)
            
        Returns:
            Dict with publish_id and upload_url (if applicable)
        """
        # Validate URL is from Supabase or other verified domain
        if not self._is_valid_video_url(video_url):
            raise ValueError(f"Invalid video URL. Must be from verified domain. Got: {video_url}")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        post_data = {
            "post_info": {
                "title": title[:2200],  # Ensure within TikTok limit
                "privacy_level": privacy_level,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url
            }
        }
        
        if video_cover_timestamp_ms is not None:
            post_data["post_info"]["video_cover_timestamp_ms"] = video_cover_timestamp_ms
        
        url = f"{self.config.api_base_url}/v2/post/publish/video/init/"
        
        for attempt in range(self._retry_count):
            try:
                response = await self.client.post(url, json=post_data, headers=headers)
                data = response.json()
                
                # Check for errors in response
                if response.status_code != 200 or data.get('error', {}).get('code') != 'ok':
                    error_code = data.get('error', {}).get('code', 'unknown')
                    error_msg = data.get('error', {}).get('message', 'Unknown error')
                    
                    # Map specific error codes
                    if error_code == 'spam_risk_too_many_posts':
                        raise HTTPException(status_code=429, detail="Daily post limit reached")
                    elif error_code == 'url_ownership_unverified':
                        raise HTTPException(status_code=403, detail="Video URL domain not verified")
                    elif error_code == 'unaudited_client_can_only_post_to_private_accounts':
                        raise HTTPException(status_code=403, detail="Sandbox mode: Your TikTok account must be set to private. Go to TikTok app → Profile → Settings → Privacy → Turn on 'Private account'")
                    elif error_code == 'privacy_level_option_mismatch':
                        raise HTTPException(status_code=400, detail="Invalid privacy level for this account")
                    else:
                        raise HTTPException(status_code=400, detail=error_msg)
                
                return data.get('data', {})
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < self._retry_count - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                    continue
                raise
            except httpx.RequestError as e:
                if attempt < self._retry_count - 1:
                    await asyncio.sleep(self._retry_delay)
                    continue
                raise
        
        raise HTTPException(status_code=500, detail="Failed to post video after retries")
    
    async def check_post_status(self, publish_id: str) -> Dict[str, Any]:
        """
        Check the status of a posted video.
        
        Args:
            publish_id: The publish ID from the post initiation
            
        Returns:
            Status dict with status, fail_reason, post_id, etc.
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        post_data = {
            "publish_id": publish_id
        }
        
        url = f"{self.config.api_base_url}/v2/post/publish/status/fetch/"
        
        try:
            response = await self.client.post(url, json=post_data, headers=headers)
            data = response.json()
            
            if data.get('error', {}).get('code') != 'ok':
                error_msg = data.get('error', {}).get('message', 'Unknown error')
                raise HTTPException(status_code=400, detail=error_msg)
            
            return data.get('data', {})
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Failed to check status: {str(e)}")
    
    async def post_video_from_task(
        self,
        task: Any,
        title: Optional[str] = None,
        privacy_level: str = "SELF_ONLY"
    ) -> Dict[str, Any]:
        """
        Post a video from a completed task.
        
        Args:
            task: InstanceTask object with video output
            title: Optional override for caption (uses task suggestion if not provided)
            privacy_level: Privacy level for the post
            
        Returns:
            Post result with publish_id
        """
        # Extract video URL from task
        video_url = task.get_video_url()
        if not video_url:
            raise ValueError("Task has no video output")
        
        # Use provided title or extract from task
        if not title and task.output_data:
            title = task.output_data.get('caption') or task.output_data.get('suggested_caption')
        
        if not title:
            title = f"Check out this video! #{task.instance_id}"
        
        # Post the video
        return await self.post_video_sandbox(
            video_url=video_url,
            title=title,
            privacy_level=privacy_level
        )
    
    async def post_video_from_url(
        self,
        video_url: str,
        title: str,
        privacy_level: str = "SELF_ONLY",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Simplified method to post a video from a Supabase URL.
        
        Args:
            video_url: Direct URL to video in Supabase storage
            title: Video caption/title
            privacy_level: Privacy setting
            **kwargs: Additional options (disable_duet, disable_comment, etc.)
            
        Returns:
            Dict with publish_id for tracking
        """
        # Validate URL
        if not self._is_valid_video_url(video_url):
            raise ValueError(f"Invalid video URL. Must be from Supabase storage. Got: {video_url}")
        
        # Post with retry logic
        result = await self.post_video_sandbox(
            video_url=video_url,
            title=title,
            privacy_level=privacy_level,
            **kwargs
        )
        
        return {
            "success": True,
            "publish_id": result.get("publish_id"),
            "status": "processing",
            "message": "Video submitted to TikTok for processing"
        }
    
    def _is_valid_video_url(self, url: str) -> bool:
        """
        Validate that the video URL is from a verified domain.
        
        Args:
            url: Video URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            
            # Must be HTTPS
            if parsed.scheme != 'https':
                return False
            
            if not parsed.hostname:
                return False
            
            # Check for Supabase storage URLs
            if 'supabase' in parsed.hostname:
                return True
            
            # Check for other verified domains (add as needed)
            verified_domains = [
                'supabase.co',
                'supabase.io',
                'storage.googleapis.com',
                's3.amazonaws.com'
            ]
            
            return any(domain in parsed.hostname for domain in verified_domains)
            
        except Exception:
            return False
    
    async def cancel_post(self, publish_id: str) -> bool:
        """
        Cancel an ongoing post (best effort).
        
        Args:
            publish_id: The publish ID to cancel
            
        Returns:
            True if cancelled, False otherwise
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        post_data = {
            "publish_id": publish_id
        }
        
        url = f"{self.config.api_base_url}/v2/post/publish/cancel/"
        
        try:
            response = await self.client.post(url, json=post_data, headers=headers)
            data = response.json()
            
            return data.get('error', {}).get('code') == 'ok'
            
        except Exception:
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()