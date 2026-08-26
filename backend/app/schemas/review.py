from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ReviewQuestionAnswers(BaseModel):
    completed_notes: Optional[str] = ""
    missed_reasons: Optional[str] = ""
    tomorrow_priorities: Optional[str] = ""
    deadline_changes: Optional[str] = ""
    energy_rating: int = Field(default=3, ge=1, le=5)
    task_statuses: Optional[Dict[int, str]] = None


class DailyReviewCreate(BaseModel):
    review_date: Optional[date] = None
    energy_rating: int = Field(default=3, ge=1, le=5)
    completed_notes: Optional[str] = ""
    missed_reasons: Optional[str] = ""
    tomorrow_priorities: Optional[str] = ""
    deadline_changes: Optional[str] = ""
    task_statuses: Optional[Dict[int, str]] = None


class DailyReviewResponse(BaseModel):
    id: int
    user_id: int
    review_date: date
    energy_rating: int
    completed_notes: Optional[str]
    missed_reasons: Optional[str]
    tomorrow_priorities: Optional[str]
    deadline_changes: Optional[str]
    ai_analysis_summary: Optional[str]
    xp_awarded: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TodaySummaryResponse(BaseModel):
    date: date
    scheduled_tasks: List[Any]
    completed_tasks: List[Any]
    missed_tasks: List[Any]
    partial_tasks: List[Any]
    total_xp_today: int
    current_level: int
    total_xp: int
    upcoming_deadlines: List[Any]
