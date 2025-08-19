"""
Simplified TikTok MVP API endpoints for testing.

This module provides minimal endpoints for posting task outputs to TikTok,
focused on core functionality without complex error handling or multi-account support.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.api.deps import get_current_user_id
from src.models.instance import InstanceTask, InstanceTaskStatus
from src.services.tiktok.content_api import TikTokContentAPI
from src.services.tiktok.config import tiktok_config


router = APIRouter(prefix="/api/v1/tiktok-mvp", tags=["tiktok-mvp"])


class SimpleTikTokPostRequest(BaseModel):
    """Simplified request for posting to TikTok."""
    title: str
    video_url: Optional[str] = None  # If not provided, will try to get from task
    privacy_level: str = "SELF_ONLY"  # Default to private for testing


class SimpleTikTokPostResponse(BaseModel):
    """Simplified response for TikTok posting."""
    success: bool
    publish_id: Optional[str] = None
    message: str
    task_id: Optional[UUID] = None


@router.post("/test-post", response_model=SimpleTikTokPostResponse)
async def test_tiktok_post(
    request: SimpleTikTokPostRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Test endpoint for posting a video to TikTok.
    
    This is a simplified MVP endpoint that uses hardcoded credentials
    and minimal error handling for testing purposes.
    """
    # For MVP, use hardcoded test credentials
    # In production, get from database
    test_access_token = "test_token_here"  # TODO: Set from env or database
    test_open_id = "test_open_id_here"     # TODO: Set from env or database
    
    if not request.video_url:
        return SimpleTikTokPostResponse(
            success=False,
            message="Video URL is required for MVP testing"
        )
    
    try:
        # Initialize content API with test credentials
        content_api = TikTokContentAPI(
            access_token=test_access_token,
            open_id=test_open_id
        )
        
        # Post video
        result = await content_api.post_video_from_url(
            video_url=request.video_url,
            title=request.title,
            privacy_level=request.privacy_level
        )
        
        return SimpleTikTokPostResponse(
            success=result.get("success", False),
            publish_id=result.get("publish_id"),
            message=result.get("message", "Posted to TikTok")
        )
        
    except Exception as e:
        return SimpleTikTokPostResponse(
            success=False,
            message=f"Error: {str(e)}"
        )


@router.post("/tasks/{task_id}/simple-post", response_model=SimpleTikTokPostResponse)
async def simple_post_task_to_tiktok(
    task_id: UUID,
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Simplified endpoint to post a task's video output to TikTok.
    
    MVP version with minimal complexity for testing.
    """
    # Get task
    task = db.query(InstanceTask).filter(
        InstanceTask.id == task_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Basic validation
    if task.status != InstanceTaskStatus.COMPLETED:
        return SimpleTikTokPostResponse(
            success=False,
            message=f"Task must be completed (current: {task.status})",
            task_id=task_id
        )
    
    # Get video URL from task output
    video_url = None
    if task.output_data:
        video_url = task.output_data.get("video_url")
    
    if not video_url:
        return SimpleTikTokPostResponse(
            success=False,
            message="Task has no video output",
            task_id=task_id
        )
    
    # Use provided title or get from task
    if not title and task.output_data:
        title = task.output_data.get("suggested_caption", "Check out this video!")
    elif not title:
        title = "Posted from Swallowtail"
    
    # For MVP, use test credentials
    test_access_token = "test_token_here"  # TODO: Set from env
    test_open_id = "test_open_id_here"     # TODO: Set from env
    
    try:
        content_api = TikTokContentAPI(
            access_token=test_access_token,
            open_id=test_open_id
        )
        
        result = await content_api.post_video_from_url(
            video_url=video_url,
            title=title,
            privacy_level="SELF_ONLY"  # Always private for MVP
        )
        
        # Update task with publish ID (simplified)
        if result.get("success") and result.get("publish_id"):
            task.tiktok_publish_id = result["publish_id"]
            task.tiktok_post_status = "PROCESSING"
            db.commit()
        
        return SimpleTikTokPostResponse(
            success=result.get("success", False),
            publish_id=result.get("publish_id"),
            message=result.get("message", "Posted to TikTok"),
            task_id=task_id
        )
        
    except Exception as e:
        return SimpleTikTokPostResponse(
            success=False,
            message=f"Error: {str(e)}",
            task_id=task_id
        )


@router.get("/tasks/{task_id}/simple-status")
async def simple_check_tiktok_status(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Simple status check for a TikTok post.
    
    MVP version that returns basic status information.
    """
    # Get task
    task = db.query(InstanceTask).filter(
        InstanceTask.id == task_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not task.tiktok_publish_id:
        return {
            "status": "NOT_POSTED",
            "message": "Task has not been posted to TikTok"
        }
    
    # For MVP, simulate status check
    # In production, would call TikTok API
    if tiktok_config.sandbox_mode:
        # Simulate completion after posting
        if task.tiktok_post_status == "PROCESSING":
            task.tiktok_post_status = "PUBLISHED"
            task.tiktok_post_url = f"https://www.tiktok.com/@test/video/{task.tiktok_publish_id}"
            db.commit()
    
    return {
        "status": task.tiktok_post_status,
        "publish_id": task.tiktok_publish_id,
        "post_url": task.tiktok_post_url,
        "message": f"Post is {task.tiktok_post_status.lower()}"
    }


@router.get("/test-connection")
async def test_tiktok_connection():
    """
    Test endpoint to verify TikTok API connection.
    
    Returns basic configuration info (safe to expose).
    """
    return {
        "sandbox_mode": tiktok_config.sandbox_mode,
        "api_base_url": tiktok_config.api_base_url,
        "redirect_uri": tiktok_config.redirect_uri,
        "configured": bool(tiktok_config.client_key),
        "message": "TikTok MVP endpoints ready for testing"
    }