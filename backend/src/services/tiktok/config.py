"""TikTok API configuration."""
from pydantic import BaseModel
from src.core.config import get_settings

settings = get_settings()


class TikTokConfig(BaseModel):
    """TikTok API configuration."""
    
    client_key: str
    client_secret: str
    redirect_uri: str
    sandbox_mode: bool = True
    
    # OAuth endpoints
    auth_base_url: str = "https://www.tiktok.com"
    api_base_url: str = "https://open.tiktokapis.com"
    
    # OAuth paths
    authorize_path: str = "/v2/auth/authorize/"
    token_path: str = "/v2/oauth/token/"
    user_info_path: str = "/v2/user/info/"
    
    # Content API paths
    video_upload_path: str = "/v2/post/publish/video/init/"
    
    # Scopes
    default_scopes: list[str] = [
        "user.info.basic",
        "user.info.profile", 
        "user.info.stats",
        "video.list",
        "video.publish"
    ]
    
    @property
    def authorize_url(self) -> str:
        """Get full authorization URL."""
        return f"{self.auth_base_url}{self.authorize_path}"
    
    @property
    def token_url(self) -> str:
        """Get full token URL."""
        return f"{self.api_base_url}{self.token_path}"
    
    @property
    def user_info_url(self) -> str:
        """Get full user info URL."""
        return f"{self.api_base_url}{self.user_info_path}"


# Initialize config from environment
tiktok_config = TikTokConfig(
    client_key=getattr(settings, 'tiktok_client_key', '') or '',
    client_secret=getattr(settings, 'tiktok_client_secret', '') or '',
    redirect_uri=getattr(settings, 'tiktok_redirect_uri', 'https://skipper-ecom.com/tiktok/callback'),
    sandbox_mode=getattr(settings, 'tiktok_sandbox_mode', True)
)