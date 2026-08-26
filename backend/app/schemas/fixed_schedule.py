from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FixedScheduleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM format, e.g. 07:30")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM format, e.g. 12:50")
    days_of_week: str = Field(default="mon,tue,wed,thu,fri,sat,sun")
    is_active: bool = Field(default=True)


class FixedScheduleCreate(FixedScheduleBase):
    pass


class FixedScheduleUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    days_of_week: Optional[str] = None
    is_active: Optional[bool] = None


class FixedScheduleResponse(FixedScheduleBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
