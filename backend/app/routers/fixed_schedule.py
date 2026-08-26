from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import FixedSchedule, User
from app.schemas import FixedScheduleCreate, FixedScheduleUpdate, FixedScheduleResponse

router = APIRouter(prefix="/api/fixed-schedule", tags=["Fixed Schedule"])


def get_or_create_default_user(db: Session) -> User:
    user = db.query(User).first()
    if not user:
        user = User(username="Hero", current_level=12, total_xp=170)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("", response_model=List[FixedScheduleResponse])
def list_fixed_schedules(active_only: bool = True, db: Session = Depends(get_db)):
    """Retrieve all fixed daily schedule blocks (Gym, College, Lunch, etc.)."""
    user = get_or_create_default_user(db)
    query = db.query(FixedSchedule).filter(FixedSchedule.user_id == user.id)
    if active_only:
        query = query.filter(FixedSchedule.is_active.is_(True))
    return query.order_by(FixedSchedule.start_time).all()


@router.post("", response_model=FixedScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_fixed_schedule(schedule_in: FixedScheduleCreate, db: Session = Depends(get_db)):
    """Add a new fixed recurring block."""
    user = get_or_create_default_user(db)
    # Check start_time < end_time
    if schedule_in.start_time >= schedule_in.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be earlier than end_time",
        )
    schedule = FixedSchedule(
        user_id=user.id,
        title=schedule_in.title,
        start_time=schedule_in.start_time,
        end_time=schedule_in.end_time,
        days_of_week=schedule_in.days_of_week,
        is_active=schedule_in.is_active,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.put("/{schedule_id}", response_model=FixedScheduleResponse)
def update_fixed_schedule(
    schedule_id: int,
    schedule_in: FixedScheduleUpdate,
    db: Session = Depends(get_db),
):
    """Modify an existing fixed schedule block."""
    schedule = db.query(FixedSchedule).filter(FixedSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixed schedule not found")

    update_data = schedule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)

    if schedule.start_time >= schedule.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be earlier than end_time",
        )

    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fixed_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Delete a fixed schedule block."""
    schedule = db.query(FixedSchedule).filter(FixedSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixed schedule not found")
    db.delete(schedule)
    db.commit()
    return None
