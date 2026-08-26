from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class DailyReview(Base):
    __tablename__ = "daily_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_date = Column(Date, default=date.today, index=True)
    energy_rating = Column(Integer, default=3)
    completed_notes = Column(Text, nullable=True)
    missed_reasons = Column(Text, nullable=True)
    tomorrow_priorities = Column(Text, nullable=True)
    deadline_changes = Column(Text, nullable=True)
    ai_analysis_summary = Column(Text, nullable=True)
    xp_awarded = Column(Integer, default=50)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="daily_reviews")
