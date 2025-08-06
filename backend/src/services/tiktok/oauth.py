"""TikTok OAuth implementation."""
import secrets
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode
import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.tiktok.config import tiktok_config
from src.services.tiktok.models import (
    TikTokTokenResponse, 
    TikTokUserInfo,
    TikTokCredentials
)
from src.core.config import get_settings
from src.models.instance import Instance

settings = get_settings()


class TikTokOAuthService:
    """Service for handling TikTok OAuth flow."""
    
    def __init__(self):
        self.config = tiktok_config
        self.client = httpx.AsyncClient()
        
    async def generate_auth_url(self, instance_id: str, scopes: Optional[list[str]] = None, account_name: Optional[str] = None) -> tuple[str, str]:
        """
        Generate TikTok authorization URL with CSRF state token.
        
        Returns:
            tuple: (auth_url, state_token)
        """
        # Generate CSRF state token - include instance_id for callback
        csrf_token = secrets.token_urlsafe(32)
        # Create state that includes instance_id and csrf token
        state_parts = [instance_id, csrf_token]
        if account_name:
            state_parts.append(account_name)
        state = ":".join(state_parts)
        
        # Use default scopes if not provided
        if not scopes:
            scopes = self.config.default_scopes
            
        # Build authorization URL parameters
        params = {
            'client_key': self.config.client_key,
            'response_type': 'code',
            'scope': ','.join(scopes),
            'redirect_uri': self.config.redirect_uri,
            'state': state
        }
        
        # Construct full authorization URL
        auth_url = f"{self.config.authorize_url}?{urlencode(params)}"
        
        return auth_url, state
    
    async def exchange_code_for_token(self, code: str, redirect_uri: Optional[str] = None) -> TikTokTokenResponse:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from TikTok callback
            redirect_uri: Must match the redirect URI used in authorization request
            
        Returns:
            TikTokTokenResponse with access and refresh tokens
        """
        if not redirect_uri:
            redirect_uri = self.config.redirect_uri
            
        # Prepare token request - must be application/x-www-form-urlencoded
        data = {
            'client_key': self.config.client_key,
            'client_secret': self.config.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }
        
        try:
            response = await self.client.post(
                self.config.token_url,
                data=data,  # httpx will encode as form data
                headers=headers
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            # Check for error response
            if 'error' in token_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"TikTok OAuth error: {token_data.get('error_description', token_data['error'])}"
                )
                
            return TikTokTokenResponse(**token_data)
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to exchange code for token: {str(e)}"
            )
    
    async def refresh_access_token(self, refresh_token: str) -> TikTokTokenResponse:
        """
        Refresh an access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            TikTokTokenResponse with new tokens
        """
        data = {
            'client_key': self.config.client_key,
            'client_secret': self.config.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }
        
        try:
            response = await self.client.post(
                self.config.token_url,
                data=data,
                headers=headers
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            if 'error' in token_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"TikTok refresh error: {token_data.get('error_description', token_data['error'])}"
                )
                
            return TikTokTokenResponse(**token_data)
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to refresh token: {str(e)}"
            )
    
    async def get_user_info(self, access_token: str) -> TikTokUserInfo:
        """
        Get TikTok user information.
        
        Args:
            access_token: Valid access token
            
        Returns:
            TikTokUserInfo with user details
        """
        # Query user info with required fields
        params = {
            'fields': 'open_id,union_id,avatar_url,avatar_url_100,avatar_large_url,display_name,bio_description,profile_deep_link,is_verified,follower_count,following_count,likes_count,video_count'
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            response = await self.client.get(
                self.config.user_info_url,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data and data['error']['code'] != 'ok':
                raise HTTPException(
                    status_code=400,
                    detail=f"TikTok API error: {data['error']['message']}"
                )
                
            # Extract user data from response
            user_data = data.get('data', {}).get('user', {})
            return TikTokUserInfo(**user_data)
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get user info: {str(e)}"
            )
    
    async def revoke_access(self, access_token: str) -> bool:
        """
        Revoke access token.
        
        Args:
            access_token: Token to revoke
            
        Returns:
            True if successful
        """
        data = {
            'client_key': self.config.client_key,
            'client_secret': self.config.client_secret,
            'token': access_token
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }
        
        try:
            response = await self.client.post(
                f"{self.config.api_base_url}/v2/oauth/revoke/",
                data=data,
                headers=headers
            )
            response.raise_for_status()
            
            # Successful revocation returns empty response
            return True
            
        except httpx.HTTPError:
            return False
    
    def verify_state(self, state: str, expected_state: str) -> bool:
        """
        Verify CSRF state token matches.
        
        Args:
            state: State from callback
            expected_state: State we generated
            
        Returns:
            True if valid
        """
        return secrets.compare_digest(state, expected_state)
    
    async def save_credentials(
        self, 
        db: AsyncSession,
        instance_id: str,
        token_response: TikTokTokenResponse,
        user_info: Optional[TikTokUserInfo] = None,
        account_name: Optional[str] = None
    ) -> 'InstanceTikTokCredentials':
        """
        Save TikTok credentials to database.
        
        Args:
            db: Database session
            instance_id: Instance UUID
            token_response: Token response from TikTok
            user_info: Optional user information
            
        Returns:
            InstanceTikTokCredentials object
        """
        from src.models.tiktok_credentials import InstanceTikTokCredentials
        from sqlalchemy import select
        from uuid import UUID
        
        # Calculate token expiration times
        now = datetime.utcnow()
        access_token_expires_at = now + timedelta(seconds=token_response.expires_in)
        refresh_token_expires_at = now + timedelta(seconds=token_response.refresh_expires_in)
        
        # Check if credentials already exist for this instance and TikTok account
        stmt = select(InstanceTikTokCredentials).where(
            InstanceTikTokCredentials.instance_id == UUID(instance_id),
            InstanceTikTokCredentials.tiktok_open_id == token_response.open_id
        )
        existing = await db.execute(stmt)
        credentials = existing.scalar_one_or_none()
        
        if credentials:
            # Update existing credentials
            credentials.tiktok_open_id = token_response.open_id
            credentials.display_name = user_info.display_name if user_info else token_response.open_id
            credentials.avatar_url = user_info.avatar_url if user_info else None
            credentials.access_token = token_response.access_token
            credentials.refresh_token = token_response.refresh_token
            credentials.access_token_expires_at = access_token_expires_at
            credentials.refresh_token_expires_at = refresh_token_expires_at
            credentials.scopes = token_response.scope.split(',')
            credentials.user_info = user_info.model_dump() if user_info else None
            credentials.is_active = "active"
            credentials.updated_at = now
        else:
            # Create new credentials
            credentials = InstanceTikTokCredentials(
                instance_id=UUID(instance_id),
                tiktok_open_id=token_response.open_id,
                tiktok_union_id=user_info.union_id if user_info else None,
                display_name=user_info.display_name if user_info else token_response.open_id,
                account_name=account_name,
                avatar_url=user_info.avatar_url if user_info else None,
                access_token=token_response.access_token,
                refresh_token=token_response.refresh_token,
                access_token_expires_at=access_token_expires_at,
                refresh_token_expires_at=refresh_token_expires_at,
                scopes=token_response.scope.split(','),
                user_info=user_info.model_dump() if user_info else None,
                is_active="active"
            )
            db.add(credentials)
        
        await db.commit()
        await db.refresh(credentials)
        
        return credentials
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()