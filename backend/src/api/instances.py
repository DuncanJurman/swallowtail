"""API endpoints for instance management."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.sync_database import get_db
from src.services.instance_service import InstanceService
from src.models.instance_schemas import (
    InstanceCreate, InstanceResponse, TaskSubmission, InstanceTaskResponse
)
from src.models.instance import InstanceTaskStatus


router = APIRouter(prefix="/instances", tags=["instances"])


def get_current_user_id() -> UUID:
    """Get the current user ID from auth context."""
    # TODO: Implement actual authentication
    # For now, return a fixed UUID for testing
    return UUID("00000000-0000-0000-0000-000000000001")


@router.post("/", response_model=InstanceResponse, status_code=status.HTTP_201_CREATED)
def create_instance(
    instance_data: InstanceCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a new instance for the current user."""
    service = InstanceService(db)
    instance = service.create_instance(user_id, instance_data)
    return instance


@router.get("/", response_model=List[InstanceResponse])
def list_instances(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """List all instances for the current user."""
    service = InstanceService(db)
    instances = service.list_instances(user_id)
    return instances


@router.get("/{instance_id}", response_model=InstanceResponse)
def get_instance(
    instance_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get a specific instance by ID."""
    service = InstanceService(db)
    instance = service.get_instance(instance_id, user_id)
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    
    return instance


@router.patch("/{instance_id}", response_model=InstanceResponse)
def update_instance(
    instance_id: UUID,
    updates: dict,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Update instance properties."""
    service = InstanceService(db)
    instance = service.update_instance(instance_id, user_id, updates)
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    
    return instance


@router.post("/{instance_id}/tasks", response_model=InstanceTaskResponse, status_code=status.HTTP_201_CREATED)
def submit_task(
    instance_id: UUID,
    task_data: TaskSubmission,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Submit a new task to an instance."""
    service = InstanceService(db)
    task = service.submit_task(instance_id, user_id, task_data)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    
    return task


@router.get("/{instance_id}/tasks", response_model=List[InstanceTaskResponse])
def list_tasks(
    instance_id: UUID,
    status: InstanceTaskStatus = None,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """List tasks for an instance, optionally filtered by status."""
    service = InstanceService(db)
    tasks = service.get_instance_tasks(instance_id, user_id, status)
    
    if tasks is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    
    return tasks