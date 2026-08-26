from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class DailyPlan(Base):
    __tablename__ = "daily_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_date = Column(Date, nullable=False, index=True)
    status = Column(String(30), default="DRAFT")
    total_planned_minutes = Column(Integer, default=0)
    total_potential_xp = Column(Integer, default=0)
    ai_reasoning = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=utc_now)
    approved_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="daily_plans")
    scheduled_blocks = relationship("ScheduledBlock", back_populates="plan", cascade="all, delete-orphan", order_by="ScheduledBlock.start_time")


class ScheduledBlock(Base):
    __tablename__ = "scheduled_blocks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("daily_plans.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    title = Column(String(200), nullable=False)
    block_type = Column(String(30), default="TASK")
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(30), default="PENDING")
    xp_earned = Column(Integer, default=0)
    display_order = Column(Integer, default=0)

    plan = relationship("DailyPlan", back_populates="scheduled_blocks")
    task = relationship("Task", back_populates="scheduled_blocks")
