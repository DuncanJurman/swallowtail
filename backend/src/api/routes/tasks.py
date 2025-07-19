"""API routes for product task management."""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.database import get_db
from ...core.state import SharedState
from ...models.database import ProductTask, Product, TaskStatus
from ...models.task import (
    TaskCreateRequest,
    TaskResponse,
    TaskListResponse,
    TaskStatusUpdate,
    TaskUpdateRequest,
)
from ...agents.product_orchestrator import ProductOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["tasks"])


@router.post("/products/{product_id}/tasks", response_model=TaskResponse)
async def create_task(
    product_id: UUID,
    task_data: TaskCreateRequest,
    db: AsyncSession = Depends(get_db),
    auto_execute: bool = Query(False, description="Automatically execute the task after creation"),
) -> TaskResponse:
    """Create a new task for a product."""
    # Verify product exists
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create new task
    new_task = ProductTask(
        product_id=product_id,
        task_description=task_data.task_description,
        priority=task_data.priority.value,
        status=TaskStatus.PENDING,
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    logger.info(f"Created task {new_task.id} for product {product_id}")
    
    # Notify the system about new task (for real-time updates)
    shared_state = SharedState()
    await shared_state.set(f"new_task:{product_id}", str(new_task.id))
    
    # Auto-execute if requested
    if auto_execute:
        logger.info(f"Auto-executing task {new_task.id}")
        orchestrator = ProductOrchestrator()
        
        # Start execution in background (fire and forget)
        import asyncio
        asyncio.create_task(
            orchestrator.execute_task(
                task_id=new_task.id,
                task_description=new_task.task_description,
                product_id=new_task.product_id
            )
        )
    
    return TaskResponse.model_validate(new_task)


@router.get("/products/{product_id}/tasks", response_model=TaskListResponse)
async def list_product_tasks(
    product_id: UUID,
    status: Optional[TaskStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    """List all tasks for a product with optional filtering."""
    # Build query
    query = select(ProductTask).where(ProductTask.product_id == product_id)
    
    if status:
        query = query.where(ProductTask.status == status)
    
    # Add ordering - most recent first, then by priority
    query = query.order_by(ProductTask.created_at.desc(), ProductTask.priority)
    
    # Count total tasks
    count_query = select(func.count()).select_from(ProductTask).where(ProductTask.product_id == product_id)
    if status:
        count_query = count_query.where(ProductTask.status == status)
    
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Get details of a specific task."""
    query = select(ProductTask).where(ProductTask.id == task_id).options(
        selectinload(ProductTask.product)
    )
    
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse.model_validate(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    update_data: TaskUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update a task's details."""
    # Get existing task
    result = await db.execute(select(ProductTask).where(ProductTask.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields if provided
    if update_data.status is not None:
        task.status = update_data.status
        
        # Update timestamps based on status
        if update_data.status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.now(timezone.utc)
        elif update_data.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            task.completed_at = datetime.now(timezone.utc)
    
    if update_data.priority is not None:
        task.priority = update_data.priority.value
        
    if update_data.assigned_agent is not None:
        task.assigned_agent = update_data.assigned_agent
        
    if update_data.result_data is not None:
        task.result_data = update_data.result_data
        
    if update_data.error_message is not None:
        task.error_message = update_data.error_message
    
    await db.commit()
    await db.refresh(task)
    
    logger.info(f"Updated task {task_id}")
    
    return TaskResponse.model_validate(task)


@router.put("/tasks/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: UUID,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update only the status of a task (convenience endpoint)."""
    # Get existing task
    result = await db.execute(select(ProductTask).where(ProductTask.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update status
    task.status = status_update.status
    
    # Update timestamps
    if status_update.status == TaskStatus.IN_PROGRESS and not task.started_at:
        task.started_at = datetime.now(timezone.utc)
    elif status_update.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        task.completed_at = datetime.now(timezone.utc)
        
    # Update optional fields
    if status_update.message:
        if status_update.status == TaskStatus.FAILED:
            task.error_message = status_update.message
            
    if status_update.result_data:
        task.result_data = status_update.result_data
    
    await db.commit()
    await db.refresh(task)
    
    logger.info(f"Updated task {task_id} status to {status_update.status}")
    
    # Notify about status change
    shared_state = SharedState()
    await shared_state.set(
        f"task_status_change:{task.product_id}:{task_id}", 
        status_update.status.value
    )
    
    return TaskResponse.model_validate(task)


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a task (only if in PENDING status)."""
    # Get existing task
    result = await db.execute(select(ProductTask).where(ProductTask.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only allow deletion of pending tasks
    if task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=400, 
            detail="Can only delete tasks in PENDING status"
        )
    
    await db.delete(task)
    await db.commit()
    
    logger.info(f"Deleted task {task_id}")
    
    return {"message": "Task deleted successfully"}


@router.post("/tasks/{task_id}/execute")
async def execute_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Execute a pending task using the Product Orchestrator."""
    # Get the task
    result = await db.execute(
        select(ProductTask).where(ProductTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only execute pending tasks
    if task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Task is {task.status.value}, can only execute PENDING tasks"
        )
    
    # Create orchestrator and execute
    orchestrator = ProductOrchestrator()
    
    # Execute the task asynchronously
    result = await orchestrator.execute_task(
        task_id=task_id,
        task_description=task.task_description,
        product_id=task.product_id
    )
    
    if result.success:
        logger.info(f"Successfully executed task {task_id}")
        return {
            "message": "Task execution started",
            "task_id": str(task_id),
            "status": "executing"
        }
    else:
        logger.error(f"Failed to execute task {task_id}: {result.error}")
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {result.error}"
        )