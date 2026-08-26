from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserPreferencesBase(BaseModel):
    wake_up_time: str = Field(default="05:00", pattern=r"^\d{2}:\d{2}$")
    sleep_time: str = Field(default="22:00", pattern=r"^\d{2}:\d{2}$")
    max_daily_work_minutes: int = Field(default=480, ge=60, le=960)
    default_break_minutes: int = Field(default=15, ge=5, le=60)
    preferred_focus_block_minutes: int = Field(default=90, ge=15, le=180)
    energy_peak_time: str = Field(default="morning")


class UserPreferencesUpdate(BaseModel):
    wake_up_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    sleep_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    max_daily_work_minutes: Optional[int] = Field(None, ge=60, le=960)
    default_break_minutes: Optional[int] = Field(None, ge=5, le=60)
    preferred_focus_block_minutes: Optional[int] = Field(None, ge=15, le=180)
    energy_peak_time: Optional[str] = None


class UserPreferencesResponse(UserPreferencesBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    username: str
    current_level: int
    total_xp: int
    created_at: datetime
    preferences: Optional[UserPreferencesResponse] = None

    model_config = ConfigDict(from_attributes=True)
