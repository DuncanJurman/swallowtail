"""Enhanced task API endpoints with filtering and queue integration."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.orm import Session

from src.core.sync_database import get_db
from src.tasks.queue_service import TaskQueueService
from src.models.instance import Instance, InstanceTask, InstanceTaskStatus, TaskPriority
from src.models.instance_schemas import (
    TaskSubmission, 
    InstanceTaskResponse, 
    TaskListFilters,
    TaskUpdateRequest,
    TaskDetailResponse,
    TaskPlanningStep,
    TaskExecutionLog,
    InstanceMediaResponse,
    TikTokPostRequest,
    TikTokPostResponse,
    TikTokPostStatusResponse
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_current_user_id() -> UUID:
    """Get the current user ID from auth context."""
    # TODO: Implement actual authentication
    # For now, return a fixed UUID for testing
    return UUID("00000000-0000-0000-0000-000000000001")


def verify_instance_access(
    instance_id: UUID,
    user_id: UUID,
    db: Session
) -> Instance:
    """Verify user has access to the instance."""
    instance = db.query(Instance).filter(
        Instance.id == instance_id,
        Instance.user_id == user_id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found or access denied"
        )
    
    return instance


def verify_task_access(
    task_id: UUID,
    user_id: UUID,
    db: Session
) -> InstanceTask:
    """Verify user has access to the task."""
    task = db.query(InstanceTask).join(Instance).filter(
        InstanceTask.id == task_id,
        Instance.user_id == user_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )
    
    return task


@router.post("/instances/{instance_id}/tasks", 
             response_model=InstanceTaskResponse,
             status_code=status.HTTP_201_CREATED)
def submit_task(
    instance_id: UUID,
    task_data: TaskSubmission,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Submit a new task to the queue."""
    # Verify access
    instance = verify_instance_access(instance_id, user_id, db)
    
    # Submit task through queue service
    queue_service = TaskQueueService(db)
    task = queue_service.submit_task(instance_id, task_data)
    
    # Process scheduled tasks in background
    if not task_data.scheduled_for or task_data.scheduled_for <= datetime.now():
        background_tasks.add_task(process_scheduled_tasks, db)
    
    return task


@router.get("/instances/{instance_id}/tasks",
            response_model=List[InstanceTaskResponse])
def list_tasks(
    instance_id: UUID,
    status: Optional[InstanceTaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    scheduled_after: Optional[datetime] = Query(None),
    scheduled_before: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """List tasks with advanced filtering."""
    # Verify access
    instance = verify_instance_access(instance_id, user_id, db)
    
    # Create filters
    filters = TaskListFilters(
        status=status,
        priority=priority,
        created_after=created_after,
        created_before=created_before,
        scheduled_after=scheduled_after,
        scheduled_before=scheduled_before,
        limit=limit,
        offset=offset
    )
    
    # Get tasks through queue service
    queue_service = TaskQueueService(db)
    tasks = queue_service.list_tasks(instance_id, filters)
    
    return tasks


@router.get("/tasks/{task_id}",
            response_model=InstanceTaskResponse)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get task details with current status."""
    task = verify_task_access(task_id, user_id, db)
    return task


@router.get("/tasks/{task_id}/status")
def get_task_status(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get detailed task status including Celery information."""
    task = verify_task_access(task_id, user_id, db)
    
    queue_service = TaskQueueService(db)
    status = queue_service.get_task_status(task_id)
    
    return status


@router.patch("/tasks/{task_id}",
              response_model=InstanceTaskResponse)
def update_task(
    task_id: UUID,
    update_data: TaskUpdateRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Update task properties (priority, status, etc)."""
    task = verify_task_access(task_id, user_id, db)
    
    queue_service = TaskQueueService(db)
    updated_task = queue_service.update_task(task_id, update_data)
    
    return updated_task


@router.post("/tasks/{task_id}/cancel",
             status_code=status.HTTP_204_NO_CONTENT)
def cancel_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Cancel a pending or running task."""
    task = verify_task_access(task_id, user_id, db)
    
    queue_service = TaskQueueService(db)
    success = queue_service.cancel_task(task_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be cancelled in its current state"
        )
    
    return


@router.post("/tasks/{task_id}/retry",
             response_model=InstanceTaskResponse)
def retry_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Retry a failed task."""
    task = verify_task_access(task_id, user_id, db)
    
    queue_service = TaskQueueService(db)
    
    try:
        retried_task = queue_service.retry_task(task_id)
        return retried_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/process-scheduled",
             include_in_schema=False)
def trigger_scheduled_processing(
    db: Session = Depends(get_db)
):
    """Manually trigger processing of scheduled tasks (admin endpoint)."""
    queue_service = TaskQueueService(db)
    count = queue_service.process_scheduled_tasks()
    
    return {"processed": count}


def process_scheduled_tasks(db: Session):
    """Background task to process scheduled tasks."""
    try:
        queue_service = TaskQueueService(db)
        queue_service.process_scheduled_tasks()
    except Exception as e:
        print(f"Error processing scheduled tasks: {e}")


# Register processors on import
def register_task_processors():
    """Register all task processors with the queue service."""
    from src.tasks.processors.default_processor import DefaultTaskProcessor
    from src.tasks.processors.content_creation_processor import ContentCreationProcessor
    
    # Register processors
    TaskQueueService.register_processor('default', DefaultTaskProcessor)
    TaskQueueService.register_processor('general', DefaultTaskProcessor)
    TaskQueueService.register_processor('content_creation', ContentCreationProcessor)


# Register processors when module is imported
register_task_processors()


# ============= New TikTok Integration Endpoints =============

@router.get("/tasks/{task_id}/detail",
            response_model=TaskDetailResponse)
def get_task_detail(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get detailed task information including planning and execution logs."""
    from src.models.instance import InstanceMedia
    
    # Verify access and get task
    task = verify_task_access(task_id, user_id, db)
    
    # Build planning steps (mock data for now - will be from parsed_intent later)
    planning_steps = []
    if task.description:
        # Generate mock planning based on task description
        if "video" in task.description.lower() or "content" in task.description.lower():
            planning_steps = [
                TaskPlanningStep(
                    id="1",
                    title="Analyze Requirements",
                    description="Parse task description and identify content type",
                    status="completed" if task.status != InstanceTaskStatus.SUBMITTED else "pending"
                ),
                TaskPlanningStep(
                    id="2", 
                    title="Generate Content",
                    description="Create video content based on requirements",
                    status="completed" if task.status in [InstanceTaskStatus.COMPLETED, InstanceTaskStatus.FAILED] else "in_progress" if task.status == InstanceTaskStatus.IN_PROGRESS else "pending"
                ),
                TaskPlanningStep(
                    id="3",
                    title="Quality Check",
                    description="Review generated content for quality",
                    status="completed" if task.status == InstanceTaskStatus.COMPLETED else "pending"
                )
            ]
    
    # Convert execution_steps to logs
    execution_logs = []
    if task.execution_steps:
        for step in task.execution_steps:
            if isinstance(step, dict):
                execution_logs.append(TaskExecutionLog(
                    timestamp=step.get('timestamp', task.processing_started_at or task.created_at),
                    agent_name=step.get('agent', 'System'),
                    action=step.get('action', 'Processing'),
                    status=step.get('status', 'info'),
                    message=step.get('output', {}).get('message', '') if isinstance(step.get('output'), dict) else str(step.get('output', '')),
                    details=step.get('output')
                ))
    
    # Get attached media
    attached_media = []
    if task.attached_media_ids:
        media_items = db.query(InstanceMedia).filter(
            InstanceMedia.id.in_(task.attached_media_ids)
        ).all()
        attached_media = [InstanceMediaResponse.model_validate(item) for item in media_items]
    
    # Extract suggested caption from output_data
    suggested_caption = None
    if task.output_data and isinstance(task.output_data, dict):
        suggested_caption = task.output_data.get('caption') or task.output_data.get('suggested_caption')
    
    # Check if task can post to TikTok
    can_post = task.can_post_to_tiktok()
    
    # Build response
    response = TaskDetailResponse(
        id=task.id,
        instance_id=task.instance_id,
        description=task.description,
        status=task.status,
        priority=task.priority,
        planning=planning_steps,
        execution_logs=execution_logs,
        output_format=task.output_format,
        output_data=task.output_data,
        output_media_ids=task.output_media_ids,
        suggested_caption=suggested_caption,
        attached_media=attached_media,
        tiktok_post_data=task.tiktok_post_data,
        tiktok_publish_id=task.tiktok_publish_id,
        tiktok_post_status=task.tiktok_post_status,
        tiktok_post_url=task.tiktok_post_url,
        can_post_to_tiktok=can_post,
        created_at=task.created_at,
        updated_at=task.updated_at,
        processing_started_at=task.processing_started_at,
        processing_ended_at=task.processing_ended_at,
        scheduled_post_time=task.scheduled_post_time,
        error_message=task.error_message
    )
    
    return response


@router.post("/tasks/{task_id}/post-to-tiktok",
             response_model=TikTokPostResponse)
async def post_task_to_tiktok(
    task_id: UUID,
    post_request: TikTokPostRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Post task output video to TikTok."""
    from src.models.tiktok_credentials import InstanceTikTokCredentials
    from src.services.tiktok.oauth import TikTokOAuthService
    from src.services.tiktok.content_api import TikTokContentAPI
    from datetime import timezone
    import httpx
    
    # Verify access and get task
    task = verify_task_access(task_id, user_id, db)
    
    # Check if task can be posted
    if not task.can_post_to_tiktok():
        error_msg = "Task cannot be posted to TikTok"
        if task.status != InstanceTaskStatus.COMPLETED:
            error_msg = f"Task must be completed first (current status: {task.status})"
        elif not task.get_video_url():
            error_msg = "Task has no video output"
        elif task.tiktok_post_status in ['PROCESSING', 'PUBLISHED']:
            error_msg = f"Task already posted or posting (status: {task.tiktok_post_status})"
        
        return TikTokPostResponse(
            success=False,
            status="FAILED",
            message=error_msg,
            task_id=task_id
        )
    
    # Get TikTok credentials for the instance
    query = db.query(InstanceTikTokCredentials).filter(
        InstanceTikTokCredentials.instance_id == task.instance_id
    )
    
    # If specific account requested, filter by it
    if post_request.account_id:
        query = query.filter(InstanceTikTokCredentials.id == post_request.account_id)
    
    credentials = query.first()
    
    if not credentials:
        return TikTokPostResponse(
            success=False,
            status="FAILED",
            message="No TikTok account connected for this instance",
            task_id=task_id
        )
    
    # Check if token needs refresh
    oauth_service = TikTokOAuthService()
    if credentials.is_expired():
        try:
            refreshed_tokens = await oauth_service.refresh_access_token(
                credentials.get_refresh_token()
            )
            # Update credentials
            credentials.access_token_encrypted = refreshed_tokens['access_token']
            credentials.expires_at = datetime.fromtimestamp(
                refreshed_tokens['expires_in'] + datetime.now(timezone.utc).timestamp(),
                tz=timezone.utc
            )
            if 'refresh_token' in refreshed_tokens:
                credentials.refresh_token_encrypted = refreshed_tokens['refresh_token']
                credentials.refresh_expires_at = datetime.fromtimestamp(
                    refreshed_tokens.get('refresh_expires_in', 0) + datetime.now(timezone.utc).timestamp(),
                    tz=timezone.utc
                )
            db.commit()
        except Exception as e:
            return TikTokPostResponse(
                success=False,
                status="FAILED",
                message=f"Failed to refresh TikTok token: {str(e)}",
                task_id=task_id
            )
    
    # Initialize content API
    content_api = TikTokContentAPI(
        access_token=credentials.get_access_token(),
        open_id=credentials.tiktok_open_id
    )
    
    try:
        # Query creator info first
        creator_info = await content_api.query_creator_info()
        
        # Validate privacy level
        if post_request.privacy_level not in creator_info.get('privacy_level_options', []):
            # Default to SELF_ONLY if invalid
            post_request.privacy_level = "SELF_ONLY"
        
        # Get video URL
        video_url = task.get_video_url()
        
        # Post video using PULL_FROM_URL
        result = await content_api.post_video_sandbox(
            video_url=video_url,
            title=post_request.title,
            privacy_level=post_request.privacy_level,
            disable_duet=post_request.disable_duet,
            disable_stitch=post_request.disable_stitch,
            disable_comment=post_request.disable_comment,
            video_cover_timestamp_ms=post_request.video_cover_timestamp_ms
        )
        
        # Update task with TikTok posting info
        task.update_tiktok_status(
            status="PROCESSING",
            publish_id=result['publish_id']
        )
        
        # Store full request data
        task.tiktok_post_data = {
            'request': {
                'title': post_request.title,
                'privacy_level': post_request.privacy_level,
                'disable_duet': post_request.disable_duet,
                'disable_stitch': post_request.disable_stitch,
                'disable_comment': post_request.disable_comment,
                'video_url': video_url,
                'account_id': str(credentials.id),
                'account_name': credentials.account_name
            },
            'creator_info': creator_info,
            'initiated_at': datetime.now(timezone.utc).isoformat()
        }
        
        if post_request.schedule_time:
            task.scheduled_post_time = post_request.schedule_time
        
        db.commit()
        
        return TikTokPostResponse(
            success=True,
            publish_id=result['publish_id'],
            status="PROCESSING",
            message="Video submitted to TikTok for processing",
            task_id=task_id,
            estimated_completion_time=60  # Estimate 1 minute for processing
        )
        
    except httpx.HTTPStatusError as e:
        error_msg = f"TikTok API error: {e.response.status_code}"
        if e.response.text:
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', error_msg)
            except:
                pass
        
        task.update_tiktok_status(status="FAILED", error=error_msg)
        db.commit()
        
        return TikTokPostResponse(
            success=False,
            status="FAILED",
            message=error_msg,
            task_id=task_id
        )
    
    except Exception as e:
        task.update_tiktok_status(status="FAILED", error=str(e))
        db.commit()
        
        return TikTokPostResponse(
            success=False,
            status="FAILED", 
            message=f"Failed to post to TikTok: {str(e)}",
            task_id=task_id
        )


@router.get("/tasks/{task_id}/post-status",
            response_model=TikTokPostStatusResponse)
async def get_tiktok_post_status(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Check the status of a TikTok post."""
    from src.models.tiktok_credentials import InstanceTikTokCredentials
    from src.services.tiktok.content_api import TikTokContentAPI
    from datetime import timezone
    
    # Verify access and get task
    task = verify_task_access(task_id, user_id, db)
    
    # Check if task has been posted
    if not task.tiktok_publish_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This task has not been posted to TikTok"
        )
    
    # Get TikTok credentials
    account_id = None
    if task.tiktok_post_data and isinstance(task.tiktok_post_data, dict):
        account_id = task.tiktok_post_data.get('request', {}).get('account_id')
    
    query = db.query(InstanceTikTokCredentials).filter(
        InstanceTikTokCredentials.instance_id == task.instance_id
    )
    
    if account_id:
        query = query.filter(InstanceTikTokCredentials.id == UUID(account_id))
    
    credentials = query.first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TikTok credentials not found"
        )
    
    # Initialize content API
    content_api = TikTokContentAPI(
        access_token=credentials.get_access_token(),
        open_id=credentials.tiktok_open_id
    )
    
    try:
        # Check post status
        status_result = await content_api.check_post_status(task.tiktok_publish_id)
        
        # Map TikTok status to our status
        tiktok_status = status_result.get('status', 'UNKNOWN')
        
        # Update task based on status
        if tiktok_status == 'PUBLISH_COMPLETE':
            # Get post URL if available
            post_ids = status_result.get('publicaly_available_post_id', [])
            post_url = None
            if post_ids:
                # Construct TikTok URL (format: https://www.tiktok.com/@username/video/POST_ID)
                post_url = f"https://www.tiktok.com/@{credentials.display_name}/video/{post_ids[0]}"
            
            task.update_tiktok_status(
                status="PUBLISHED",
                post_url=post_url
            )
            db.commit()
        
        elif tiktok_status == 'FAILED':
            fail_reason = status_result.get('fail_reason', 'Unknown error')
            task.update_tiktok_status(
                status="FAILED",
                error=fail_reason
            )
            db.commit()
        
        return TikTokPostStatusResponse(
            publish_id=task.tiktok_publish_id,
            status=tiktok_status,
            fail_reason=status_result.get('fail_reason'),
            post_url=task.tiktok_post_url,
            post_id=str(status_result.get('publicaly_available_post_id', [None])[0]) if status_result.get('publicaly_available_post_id') else None,
            uploaded_bytes=status_result.get('uploaded_bytes'),
            downloaded_bytes=status_result.get('downloaded_bytes'),
            last_checked=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check TikTok post status: {str(e)}"
        )