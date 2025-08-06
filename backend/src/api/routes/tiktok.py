"""TikTok API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.services.tiktok.oauth import TikTokOAuthService
from src.services.tiktok.content_api import TikTokContentService
from src.services.tiktok.models import (
    TikTokAuthRequest,
    TikTokAuthResponse,
    TikTokCallbackRequest,
    TikTokPostRequest,
    TikTokPostResponse,
    TikTokUserInfo
)

router = APIRouter(prefix="/tiktok", tags=["tiktok"])


@router.post("/auth", response_model=TikTokAuthResponse)
async def generate_auth_url(
    request: TikTokAuthRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TikTokAuthResponse:
    """
    Generate TikTok authorization URL.
    
    This endpoint initiates the OAuth flow by generating a URL
    where the user can authorize the application.
    """
    # TODO: Verify user has access to this instance
    
    async with TikTokOAuthService() as service:
        auth_url, state = await service.generate_auth_url(
            instance_id=str(request.instance_id),
            scopes=request.scopes,
            account_name=request.account_name
        )
        
        # TODO: Store state in cache/db for verification
        
        return TikTokAuthResponse(
            auth_url=auth_url,
            state=state
        )


@router.get("/callback")
async def handle_callback(
    code: str = Query(..., description="Authorization code from TikTok"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    error: Optional[str] = Query(None, description="Error code if authorization failed"),
    error_description: Optional[str] = Query(None, description="Error description"),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle TikTok OAuth callback.
    
    This endpoint is called by TikTok after user authorization.
    It exchanges the authorization code for access tokens.
    """
    # Handle error cases
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"TikTok authorization failed: {error} - {error_description or 'No description'}"
        )
    
    # TODO: Verify state from cache/db
    # Extract instance_id from state
    
    try:
        async with TikTokOAuthService() as service:
            # Exchange code for tokens
            token_response = await service.exchange_code_for_token(code)
            
            # Get user info
            user_info = await service.get_user_info(token_response.access_token)
            
            # Extract instance_id and account_name from state
            # State format: "instance_id:csrf_token:account_name" (account_name is optional)
            state_parts = state.split(':')
            
            if len(state_parts) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid state parameter format"
                )
            
            instance_id = state_parts[0]
            # account_name is optional (3rd part)
            account_name = state_parts[2] if len(state_parts) > 2 else None
            
            # Save credentials to database
            credentials = await service.save_credentials(
                db=db,
                instance_id=instance_id,
                token_response=token_response,
                user_info=user_info,
                account_name=account_name
            )
            
            # Redirect to frontend success page
            return {
                "status": "success",
                "message": "TikTok account connected successfully",
                "user": {
                    "display_name": user_info.display_name,
                    "open_id": user_info.open_id
                }
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete OAuth flow: {str(e)}"
        )


@router.get("/accounts/{instance_id}")
async def get_accounts(
    instance_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all TikTok accounts connected to an instance.
    """
    from src.models.tiktok_credentials import InstanceTikTokCredentials
    from sqlalchemy import select
    
    # TODO: Verify user has access to this instance
    
    # Get all credentials for this instance
    stmt = select(InstanceTikTokCredentials).where(
        InstanceTikTokCredentials.instance_id == instance_id
    ).order_by(InstanceTikTokCredentials.created_at)
    
    result = await db.execute(stmt)
    all_credentials = result.scalars().all()
    
    if not all_credentials:
        return []
    
    # Check each account and refresh if needed
    accounts = []
    for credentials in all_credentials:
        # Skip inactive accounts
        if credentials.is_active != "active":
            accounts.append(credentials.to_dict())
            continue
            
        # Check if token is expired
        if credentials.is_access_token_expired:
            # Try to refresh token
            try:
                async with TikTokOAuthService() as service:
                    token_response = await service.refresh_access_token(credentials.refresh_token)
                    
                    # Update credentials
                    credentials.access_token = token_response.access_token
                    credentials.refresh_token = token_response.refresh_token
                    credentials.access_token_expires_at = datetime.utcnow() + timedelta(seconds=token_response.expires_in)
                    credentials.refresh_token_expires_at = datetime.utcnow() + timedelta(seconds=token_response.refresh_expires_in)
                    
                    await db.commit()
            except Exception:
                # If refresh fails, mark as inactive
                credentials.is_active = "expired"
                await db.commit()
        
        accounts.append(credentials.to_dict())
    
    return accounts


@router.post("/post", response_model=TikTokPostResponse)
async def post_content(
    request: TikTokPostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TikTokPostResponse:
    """
    Post content to TikTok (sandbox mode).
    
    In sandbox mode, content is only visible to authorized test users.
    """
    from src.models.tiktok_credentials import InstanceTikTokCredentials
    from sqlalchemy import select
    
    # TODO: Verify user has access to this instance
    
    # Get credentials from database
    if request.account_id:
        # Use specific account
        stmt = select(InstanceTikTokCredentials).where(
            InstanceTikTokCredentials.instance_id == request.instance_id,
            InstanceTikTokCredentials.id == request.account_id
        )
    else:
        # Use first active account
        stmt = select(InstanceTikTokCredentials).where(
            InstanceTikTokCredentials.instance_id == request.instance_id,
            InstanceTikTokCredentials.is_active == "active"
        ).order_by(InstanceTikTokCredentials.created_at).limit(1)
    
    result = await db.execute(stmt)
    credentials = result.scalar_one_or_none()
    
    if not credentials:
        raise HTTPException(
            status_code=404,
            detail="No TikTok account found for this instance" if not request.account_id 
                   else f"TikTok account {request.account_id} not found"
        )
    
    # Check if token is expired
    if credentials.is_access_token_expired:
        raise HTTPException(
            status_code=401,
            detail="TikTok access token expired. Please reconnect your account."
        )
    
    access_token = credentials.access_token
    
    try:
        async with TikTokContentService() as service:
            response = await service.post_video_sandbox(
                access_token=access_token,
                title=request.title,
                video_url=request.video_url,
                privacy_level=request.privacy_level,
                disable_duet=request.disable_duet,
                disable_comment=request.disable_comment,
                disable_stitch=request.disable_stitch,
                video_cover_timestamp_ms=request.video_cover_timestamp_ms
            )
            
            return response
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to post content: {str(e)}"
        )


@router.delete("/disconnect/{instance_id}/{account_id}")
async def disconnect_account(
    instance_id: UUID,
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disconnect a specific TikTok account from an instance.
    """
    from src.models.tiktok_credentials import InstanceTikTokCredentials
    from sqlalchemy import select, delete
    
    # TODO: Verify user has access to this instance
    
    # Get credentials from database
    stmt = select(InstanceTikTokCredentials).where(
        InstanceTikTokCredentials.instance_id == instance_id,
        InstanceTikTokCredentials.id == account_id
    )
    result = await db.execute(stmt)
    credentials = result.scalar_one_or_none()
    
    if not credentials:
        raise HTTPException(
            status_code=404,
            detail=f"TikTok account {account_id} not found for this instance"
        )
    
    # Try to revoke access token
    try:
        async with TikTokOAuthService() as service:
            await service.revoke_access(credentials.access_token)
    except Exception:
        # Continue even if revocation fails
        pass
    
    # Delete credentials from database
    await db.execute(
        delete(InstanceTikTokCredentials).where(
            InstanceTikTokCredentials.id == account_id
        )
    )
    await db.commit()
    
    return {
        "status": "success",
        "message": f"TikTok account {credentials.display_name} disconnected successfully"
    }