from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DailyPlan, ScheduledBlock, User, FixedSchedule, Task, DailyReview, UserPreferences
from app.schemas import (
    DailyPlanResponse,
    DailyPlanCreate,
    ScheduledBlockResponse,
    ScheduledBlockCreate,
    ScheduledBlockUpdate,
    PlanEditValidationRequest,
    PlanEditValidationResponse,
)
from app.services import (
    generate_deterministic_schedule,
    detect_edit_conflict,
    time_to_minutes,
    minutes_to_time,
)
from app.agents import planner_agent_app, PlanState
from app.routers.fixed_schedule import get_or_create_default_user

router = APIRouter(prefix="/api/plans", tags=["Daily Plans"])


class PlanGenerateRequest(BaseModel):
    target_date: Optional[date] = None
    review_id: Optional[int] = None
    strategy: Optional[str] = "balanced"  # balanced, deep_work, backlog_cleanup


@router.post("/generate", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def generate_plan(
    req: PlanGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Core Plan Tomorrow Engine:
    Executes the LangGraph Planner Agent with deterministic constraints & Ollama reasoning.
    Retrieves database records, runs priority scoring, slots non-overlapping blocks,
    and returns a proposed DRAFT DailyPlan with full timeline and AI explanation.
    """
    user = get_or_create_default_user(db)
    target_date = req.target_date or (date.today() + timedelta(days=1))

    # Fetch DB data
    fixed_items = db.query(FixedSchedule).filter(FixedSchedule.user_id == user.id, FixedSchedule.is_active.is_(True)).all()
    tasks = db.query(Task).filter(Task.user_id == user.id, Task.status.notin_(["COMPLETED", "CANCELLED"])).all()
    pref = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
    review = None
    if req.review_id:
        review = db.query(DailyReview).filter(DailyReview.id == req.review_id).first()
    else:
        review = db.query(DailyReview).filter(DailyReview.user_id == user.id).order_by(DailyReview.id.desc()).first()

    # Invoke LangGraph Agent workflow
    initial_state: PlanState = {
        "target_date": target_date,
        "user_id": user.id,
        "strategy": req.strategy or "balanced",
        "fixed_schedules": fixed_items,
        "candidate_tasks": tasks,
        "preferences": pref,
        "review": review,
        "plan_result": None,
        "review_analysis": None,
        "plan_explanation": None,
        "is_ai_powered": False,
    }

    agent_output = await planner_agent_app.ainvoke(initial_state)
    plan_result = agent_output["plan_result"]
    explanation = agent_output["plan_explanation"]

    # Delete previous DRAFT plan for this date if present
    existing_plan = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == user.id, DailyPlan.plan_date == target_date, DailyPlan.status == "DRAFT")
        .first()
    )
    if existing_plan:
        db.delete(existing_plan)
        db.commit()

    # Create new DRAFT DailyPlan
    new_plan = DailyPlan(
        user_id=user.id,
        plan_date=target_date,
        status="DRAFT",
        total_planned_minutes=plan_result.total_planned_minutes,
        total_potential_xp=plan_result.total_potential_xp,
        ai_reasoning=explanation,
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    # Add Scheduled Blocks
    for b in plan_result.timeline_blocks:
        block = ScheduledBlock(
            plan_id=new_plan.id,
            task_id=b.get("task_id"),
            title=b["title"],
            block_type=b["block_type"],
            start_time=b["start_time"],
            end_time=b["end_time"],
            duration_minutes=b["duration_minutes"],
            status=b.get("status", "PENDING"),
            xp_earned=b.get("xp_earned", 0),
            display_order=b.get("display_order", 0),
        )
        db.add(block)
    db.commit()
    db.refresh(new_plan)

    return {
        "plan_id": new_plan.id,
        "plan_date": target_date.isoformat(),
        "status": new_plan.status,
        "total_planned_minutes": new_plan.total_planned_minutes,
        "total_potential_xp": new_plan.total_potential_xp,
        "ai_reasoning": new_plan.ai_reasoning,
        "is_ai_powered": agent_output.get("is_ai_powered", False),
        "timeline_blocks": [
            {
                "id": b.id,
                "task_id": b.task_id,
                "title": b.title,
                "block_type": b.block_type,
                "start_time": b.start_time,
                "end_time": b.end_time,
                "duration_minutes": b.duration_minutes,
                "status": b.status,
                "xp_earned": b.xp_earned,
                "display_order": b.display_order,
            }
            for b in new_plan.scheduled_blocks
        ],
        "postponed_tasks": plan_result.postponed_tasks,
    }


@router.post("/{plan_id}/regenerate", response_model=Dict[str, Any])
async def regenerate_plan(
    plan_id: int,
    db: Session = Depends(get_db),
):
    """
    Regenerates a plan proposal with fresh reasoning while respecting existing constraints.
    Does NOT destroy the existing plan until the newly generated proposal is approved.
    """
    plan = db.query(DailyPlan).filter(DailyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    return await generate_plan(PlanGenerateRequest(target_date=plan.plan_date), db=db)


@router.get("/latest", response_model=Optional[DailyPlanResponse])
def get_latest_plan(target_date: Optional[date] = None, db: Session = Depends(get_db)):
    """Retrieve the plan for a specific date (defaults to tomorrow) or latest created."""
    user = get_or_create_default_user(db)
    if not target_date:
        target_date = date.today() + timedelta(days=1)

    plan = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == user.id, DailyPlan.plan_date == target_date)
        .order_by(DailyPlan.id.desc())
        .first()
    )
    return plan


@router.get("/{plan_id}", response_model=DailyPlanResponse)
def get_plan_by_id(plan_id: int, db: Session = Depends(get_db)):
    """Retrieve a plan by its ID."""
    plan = db.query(DailyPlan).filter(DailyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


@router.post("/{plan_id}/validate-edit", response_model=PlanEditValidationResponse)
def validate_plan_edit(
    plan_id: int,
    req: PlanEditValidationRequest,
    db: Session = Depends(get_db),
):
    """
    Validates a manual edit to a block in real-time.
    Detects if moving a task collides with fixed events or other tasks and returns conflict details.
    """
    plan = db.query(DailyPlan).filter(DailyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    blocks_dict = [
        {
            "id": b.id,
            "title": b.title,
            "block_type": b.block_type,
            "start_time": b.start_time,
            "end_time": b.end_time,
        }
        for b in plan.scheduled_blocks
    ]

    conflict_res = detect_edit_conflict(
        blocks=blocks_dict,
        target_block_id=req.block_id,
        new_start_time=req.new_start_time,
        new_end_time=req.new_end_time,
    )

    conflicting_schema = None
    if conflict_res["conflicting_block"]:
        cb = conflict_res["conflicting_block"]
        block_entity = db.query(ScheduledBlock).filter(ScheduledBlock.id == cb["id"]).first()
        if block_entity:
            conflicting_schema = ScheduledBlockResponse.model_validate(block_entity)

    return PlanEditValidationResponse(
        has_conflict=conflict_res["has_conflict"],
        conflicting_block=conflicting_schema,
        message=conflict_res["message"],
        suggested_options=conflict_res["suggested_options"],
    )


@router.post("/{plan_id}/approve", response_model=DailyPlanResponse)
def approve_plan(plan_id: int, db: Session = Depends(get_db)):
    """Approve a proposed DRAFT plan, locking its status to APPROVED."""
    plan = db.query(DailyPlan).filter(DailyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    plan.status = "APPROVED"
    plan.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    """Delete a plan."""
    plan = db.query(DailyPlan).filter(DailyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return None
