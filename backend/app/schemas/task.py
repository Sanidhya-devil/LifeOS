from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(default="General")
    estimated_minutes: int = Field(default=60, ge=5, le=720)
    importance: int = Field(default=3, ge=1, le=5)
    difficulty: int = Field(default=3, ge=1, le=5)
    deadline: Optional[datetime] = None
    goal_relevance: int = Field(default=3, ge=1, le=5)
    status: str = Field(default="PENDING")
    base_xp: int = Field(default=20, ge=0)
    parent_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    estimated_minutes: Optional[int] = Field(None, ge=5, le=720)
    importance: Optional[int] = Field(None, ge=1, le=5)
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    deadline: Optional[datetime] = None
    goal_relevance: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = None
    base_xp: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(PENDING|IN_PROGRESS|COMPLETED|SKIPPED|PARTIAL|POSTPONED|CANCELLED)$")
    actual_minutes: Optional[int] = None
    notes: Optional[str] = None
