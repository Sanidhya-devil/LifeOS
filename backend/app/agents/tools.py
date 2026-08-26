from typing import List, Dict, Any, Optional
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.models import FixedSchedule, Task, UserPreferences, DailyReview, DailyPlan
from app.services import (
    calculate_task_priority,
    rank_tasks,
    generate_deterministic_schedule,
    ProposedPlanResult,
    detect_edit_conflict,
)


def get_fixed_schedule(db: Session, user_id: int) -> List[FixedSchedule]:
    """Retrieves all active fixed commitments for the user."""
    return (
        db.query(FixedSchedule)
        .filter(FixedSchedule.user_id == user_id, FixedSchedule.is_active.is_(True))
        .order_by(FixedSchedule.start_time)
        .all()
    )


def get_pending_tasks(db: Session, user_id: int) -> List[Task]:
    """Retrieves all non-completed tasks for scheduling consideration."""
    return (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.status.notin_(["COMPLETED", "CANCELLED"]))
        .order_by(Task.deadline.asc().nullslast(), Task.importance.desc())
        .all()
    )


def get_upcoming_deadlines(db: Session, user_id: int, days_ahead: int = 7) -> List[Task]:
    """Retrieves urgent tasks with deadlines within the specified window."""
    now = datetime.now(timezone.utc)
    return (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.deadline.isnot(None),
            Task.status.notin_(["COMPLETED", "CANCELLED"]),
        )
        .order_by(Task.deadline.asc())
        .all()
    )


def get_user_preferences(db: Session, user_id: int) -> Optional[UserPreferences]:
    """Retrieves scheduling preferences (wake time, sleep time, max workload)."""
    return db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()


def run_deterministic_schedule_pipeline(
    target_date: date,
    fixed_schedules: List[FixedSchedule],
    candidate_tasks: List[Task],
    preferences: Optional[UserPreferences] = None,
    review: Optional[DailyReview] = None,
) -> ProposedPlanResult:
    """Executes the full constraint-satisfying scheduling algorithm."""
    return generate_deterministic_schedule(
        target_date=target_date,
        fixed_schedules=fixed_schedules,
        candidate_tasks=candidate_tasks,
        preferences=preferences,
        review=review,
    )
