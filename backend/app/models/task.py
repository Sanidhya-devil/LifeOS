from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="General")
    estimated_minutes = Column(Integer, default=60)
    importance = Column(Integer, default=3)
    difficulty = Column(Integer, default=3)
    deadline = Column(DateTime, nullable=True)
    goal_relevance = Column(Integer, default=3)
    status = Column(String(30), default="PENDING")
    base_xp = Column(Integer, default=20)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="tasks")
    scheduled_blocks = relationship("ScheduledBlock", back_populates="task")
    completions = relationship("TaskCompletion", back_populates="task", cascade="all, delete-orphan")


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    completed_date = Column(DateTime, default=utc_now)
    status = Column(String(30), default="COMPLETED")
    actual_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    task = relationship("Task", back_populates="completions")
