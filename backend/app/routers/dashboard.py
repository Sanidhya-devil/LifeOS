from datetime import date, datetime
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DailyPlan, ScheduledBlock, User, Task, XPTransaction
from app.routers.fixed_schedule import get_or_create_default_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


class BlockStatusUpdate(BaseModel):
    block_id: int
    status: str  # COMPLETED, SKIPPED, PARTIAL, IN_PROGRESS


@router.get("/morning")
def get_morning_dashboard(target_date: Optional[date] = None, db: Session = Depends(get_db)):
    """
    Fetch the morning view for the day:
    - User level and XP
    - Main Quests
    - Complete timeline
    """
    user = get_or_create_default_user(db)
    day = target_date or date.today()

    # Look for APPROVED or ACTIVE plan for today
    plan = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == user.id, DailyPlan.plan_date == day)
        .order_by(DailyPlan.id.desc())
        .first()
    )

    blocks_data = []
    main_quests = []
    total_potential_xp = 0

    if plan:
        blocks = (
            db.query(ScheduledBlock)
            .filter(ScheduledBlock.plan_id == plan.id)
            .order_by(ScheduledBlock.start_time)
            .all()
        )
        for b in blocks:
            task = db.query(Task).filter(Task.id == b.task_id).first() if b.task_id else None
            xp = task.base_xp if task else 0
            if b.block_type == "TASK":
                total_potential_xp += xp
                main_quests.append({
                    "block_id": b.id,
                    "task_id": b.task_id,
                    "title": b.title,
                    "category": task.category if task else "General",
                    "xp": xp,
                    "status": b.status,
                    "start_time": b.start_time,
                    "end_time": b.end_time,
                })

            blocks_data.append({
                "id": b.id,
                "task_id": b.task_id,
                "title": b.title,
                "block_type": b.block_type,
                "start_time": b.start_time,
                "end_time": b.end_time,
                "duration_minutes": b.duration_minutes,
                "status": b.status,
                "xp_earned": b.xp_earned,
                "category": task.category if task else None,
            })

    return {
        "date": day,
        "user": {
            "username": user.username,
            "current_level": user.current_level,
            "total_xp": user.total_xp,
        },
        "plan_status": plan.status if plan else "NO_PLAN",
        "plan_id": plan.id if plan else None,
        "ai_reasoning": plan.ai_reasoning if plan else None,
        "total_potential_xp": total_potential_xp,
        "main_quests": main_quests,
        "timeline": blocks_data,
    }


@router.post("/block-status")
def update_block_status(update_in: BlockStatusUpdate, db: Session = Depends(get_db)):
    """Update execution status of a scheduled block and award XP if completed."""
    user = get_or_create_default_user(db)
    block = db.query(ScheduledBlock).filter(ScheduledBlock.id == update_in.block_id).first()
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")

    prev_status = block.status
    block.status = update_in.status

    if update_in.status == "COMPLETED" and prev_status != "COMPLETED":
        task = db.query(Task).filter(Task.id == block.task_id).first() if block.task_id else None
        xp = task.base_xp if task else 20
        block.xp_earned = xp
        user.total_xp += xp
        user.current_level = 10 + (user.total_xp // 100)
        db.add(XPTransaction(user_id=user.id, amount=xp, source="BLOCK_COMPLETION", reference_id=block.id))

        if task:
            task.status = "COMPLETED"

    db.commit()
    db.refresh(block)
    return {"message": "Status updated", "block_id": block.id, "status": block.status, "current_xp": user.total_xp}
