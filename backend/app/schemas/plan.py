from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ScheduledBlockBase(BaseModel):
    task_id: Optional[int] = None
    title: str
    block_type: str = Field(default="TASK", pattern="^(FIXED|TASK|BREAK|BUFFER|REST)$")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    duration_minutes: int
    status: str = Field(default="PENDING")
    xp_earned: int = Field(default=0)
    display_order: int = Field(default=0)


class ScheduledBlockCreate(ScheduledBlockBase):
    pass


class ScheduledBlockUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    duration_minutes: Optional[int] = None
    status: Optional[str] = None


class ScheduledBlockResponse(ScheduledBlockBase):
    id: int
    plan_id: int

    model_config = ConfigDict(from_attributes=True)


class DailyPlanBase(BaseModel):
    plan_date: date
    status: str = Field(default="DRAFT")
    total_planned_minutes: int = 0
    total_potential_xp: int = 0
    ai_reasoning: Optional[str] = None


class DailyPlanCreate(BaseModel):
    plan_date: date


class DailyPlanResponse(DailyPlanBase):
    id: int
    user_id: int
    generated_at: datetime
    approved_at: Optional[datetime]
    scheduled_blocks: List[ScheduledBlockResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PlanEditValidationRequest(BaseModel):
    block_id: int
    new_start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    new_end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")


class PlanEditValidationResponse(BaseModel):
    has_conflict: bool
    conflicting_block: Optional[ScheduledBlockResponse] = None
    message: str
    suggested_options: List[str] = []
