from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Task, TaskCompletion, User, XPTransaction
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate
from app.routers.fixed_schedule import get_or_create_default_user

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status (PENDING, COMPLETED, etc.)"),
    category: Optional[str] = Query(None, description="Filter by category (DSA, Project, etc.)"),
    db: Session = Depends(get_db),
):
    """Retrieve all candidate tasks for scheduling."""
    user = get_or_create_default_user(db)
    query = db.query(Task).filter(Task.user_id == user.id)
    if status:
        query = query.filter(Task.status == status)
    if category:
        query = query.filter(Task.category == category)
    return query.order_by(Task.deadline.asc().nullslast(), Task.importance.desc()).all()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    user = get_or_create_default_user(db)
    task = Task(
        user_id=user.id,
        title=task_in.title,
        description=task_in.description,
        category=task_in.category,
        estimated_minutes=task_in.estimated_minutes,
        importance=task_in.importance,
        difficulty=task_in.difficulty,
        deadline=task_in.deadline,
        goal_relevance=task_in.goal_relevance,
        status=task_in.status,
        base_xp=task_in.base_xp,
        parent_id=task_in.parent_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Fetch task details."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    """Update task metadata."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(task_id: int, status_in: TaskStatusUpdate, db: Session = Depends(get_db)):
    """Update task completion status and award XP if completed."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    prev_status = task.status
    task.status = status_in.status

    # Record completion record
    completion = TaskCompletion(
        task_id=task.id,
        status=status_in.status,
        actual_minutes=status_in.actual_minutes,
        notes=status_in.notes,
    )
    db.add(completion)

    # Award XP if newly completed
    if status_in.status == "COMPLETED" and prev_status != "COMPLETED":
        user = db.query(User).filter(User.id == task.user_id).first()
        if user:
            user.total_xp += task.base_xp
            # Simple level formula: level = 10 + total_xp // 100
            user.current_level = 10 + (user.total_xp // 100)
            xp_tx = XPTransaction(
                user_id=user.id,
                amount=task.base_xp,
                source="TASK_COMPLETION",
                reference_id=task.id,
            )
            db.add(xp_tx)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(task)
    db.commit()
    return None
