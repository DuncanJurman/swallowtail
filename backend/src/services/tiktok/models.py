"""TikTok-specific data models."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class TikTokAuthRequest(BaseModel):
    """Request model for initiating TikTok OAuth."""
    instance_id: UUID
    scopes: Optional[list[str]] = None
    account_name: Optional[str] = None  # Optional friendly name for the account


class TikTokAuthResponse(BaseModel):
    """Response model for TikTok OAuth initiation."""
    auth_url: str
    state: str


class TikTokCallbackRequest(BaseModel):
    """Request model for TikTok OAuth callback."""
    code: str
    state: str
    instance_id: Optional[UUID] = None


class TikTokTokenResponse(BaseModel):
    """Response model from TikTok token endpoint."""
    access_token: str
    expires_in: int
    open_id: str
    refresh_expires_in: int
    refresh_token: str
    scope: str
    token_type: str


class TikTokUserInfo(BaseModel):
    """TikTok user information."""
    open_id: str
    union_id: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_url_100: Optional[str] = None
    avatar_large_url: Optional[str] = None
    display_name: str
    bio_description: Optional[str] = None
    profile_deep_link: Optional[str] = None
    is_verified: bool = False
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    likes_count: Optional[int] = None
    video_count: Optional[int] = None


class TikTokCredentials(BaseModel):
    """TikTok credentials for storage."""
    instance_id: UUID
    tiktok_open_id: str
    access_token: str
    refresh_token: str
    token_expires_at: datetime
    refresh_expires_at: datetime
    scopes: list[str]
    user_info: Optional[TikTokUserInfo] = None


class TikTokPostRequest(BaseModel):
    """Request model for posting content to TikTok."""
    instance_id: UUID
    account_id: Optional[UUID] = None  # If not provided, uses first active account
    video_url: Optional[str] = None
    title: str = Field(..., max_length=150)
    privacy_level: str = "PUBLIC_TO_EVERYONE"  # PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, SELF_ONLY
    disable_duet: bool = False
    disable_comment: bool = False
    disable_stitch: bool = False
    video_cover_timestamp_ms: Optional[int] = 1000
    

class TikTokPostResponse(BaseModel):
    """Response model for TikTok content posting."""
    post_id: Optional[str] = None
    share_url: Optional[str] = None
    status: str  # "published", "processing", "failed"
    error_message: Optional[str] = None