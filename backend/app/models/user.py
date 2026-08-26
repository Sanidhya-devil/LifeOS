from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, default="Hero")
    current_level = Column(Integer, default=12)
    total_xp = Column(Integer, default=170)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    fixed_schedules = relationship("FixedSchedule", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    daily_reviews = relationship("DailyReview", back_populates="user", cascade="all, delete-orphan")
    daily_plans = relationship("DailyPlan", back_populates="user", cascade="all, delete-orphan")
    xp_transactions = relationship("XPTransaction", back_populates="user", cascade="all, delete-orphan")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    wake_up_time = Column(String(10), default="05:00")
    sleep_time = Column(String(10), default="22:00")
    max_daily_work_minutes = Column(Integer, default=480)
    default_break_minutes = Column(Integer, default=15)
    preferred_focus_block_minutes = Column(Integer, default=90)
    energy_peak_time = Column(String(20), default="morning")

    user = relationship("User", back_populates="preferences")
