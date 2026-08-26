from datetime import datetime, date, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DailyReview, Task, DailyPlan, ScheduledBlock, User, XPTransaction
from app.schemas import DailyReviewCreate, DailyReviewResponse, TodaySummaryResponse
from app.agents import ollama_client, REVIEW_ANALYSIS_SYSTEM_PROMPT
from app.routers.fixed_schedule import get_or_create_default_user

router = APIRouter(prefix="/api/reviews", tags=["Daily Reviews"])


@router.get("/today", response_model=TodaySummaryResponse)
def get_today_summary(db: Session = Depends(get_db)):
    """Retrieve today's review overview (scheduled tasks, completions, misses, current level, XP)."""
    user = get_or_create_default_user(db)
    today = date.today()

    # Find today's plan if available
    today_plan = (
        db.query(DailyPlan)
        .filter(DailyPlan.user_id == user.id, DailyPlan.plan_date == today)
        .first()
    )

    scheduled_tasks = []
    if today_plan:
        blocks = (
            db.query(ScheduledBlock)
            .filter(ScheduledBlock.plan_id == today_plan.id)
            .order_by(ScheduledBlock.start_time)
            .all()
        )
        scheduled_tasks = [
            {
                "id": b.id,
                "task_id": b.task_id,
                "title": b.title,
                "block_type": b.block_type,
                "start_time": b.start_time,
                "end_time": b.end_time,
                "status": b.status,
                "duration_minutes": b.duration_minutes,
                "xp_earned": b.xp_earned,
            }
            for b in blocks
        ]

    # Completed tasks today
    all_tasks = db.query(Task).filter(Task.user_id == user.id).all()
    completed_tasks = [t for t in all_tasks if t.status == "COMPLETED"]
    missed_tasks = [t for t in all_tasks if t.status in ["SKIPPED", "POSTPONED"]]
    partial_tasks = [t for t in all_tasks if t.status == "PARTIAL"]

    # Upcoming deadlines within next 7 days
    seven_days = datetime.now(timezone.utc) + timedelta(days=7)
    upcoming_deadlines = (
        db.query(Task)
        .filter(
            Task.user_id == user.id,
            Task.deadline.isnot(None),
            Task.deadline <= seven_days,
            Task.status != "COMPLETED",
        )
        .order_by(Task.deadline.asc())
        .all()
    )

    # XP earned today from transactions
    start_of_day = datetime.combine(today, datetime.min.time())
    today_xp = (
        db.query(XPTransaction)
        .filter(XPTransaction.user_id == user.id, XPTransaction.created_at >= start_of_day)
        .all()
    )
    total_xp_today = sum(tx.amount for tx in today_xp)

    return TodaySummaryResponse(
        date=today,
        scheduled_tasks=scheduled_tasks,
        completed_tasks=[{"id": t.id, "title": t.title, "category": t.category, "base_xp": t.base_xp} for t in completed_tasks],
        missed_tasks=[{"id": t.id, "title": t.title, "category": t.category} for t in missed_tasks],
        partial_tasks=[{"id": t.id, "title": t.title, "category": t.category} for t in partial_tasks],
        total_xp_today=total_xp_today,
        current_level=user.current_level,
        total_xp=user.total_xp,
        upcoming_deadlines=[
            {
                "id": t.id,
                "title": t.title,
                "category": t.category,
                "deadline": t.deadline.isoformat() if t.deadline else None,
                "importance": t.importance,
            }
            for t in upcoming_deadlines
        ],
    )


@router.post("", response_model=DailyReviewResponse, status_code=status.HTTP_201_CREATED)
async def submit_daily_review(review_in: DailyReviewCreate, db: Session = Depends(get_db)):
    """Submit the nightly review reflection, analyze with AI agent, update task statuses, and award review XP."""
    user = get_or_create_default_user(db)
    target_date = review_in.review_date or date.today()

    # Update any task quick statuses passed
    if review_in.task_statuses:
        for task_id, new_status in review_in.task_statuses.items():
            task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
            if task:
                task.status = new_status
                if new_status == "COMPLETED":
                    user.total_xp += task.base_xp
                    db.add(XPTransaction(user_id=user.id, amount=task.base_xp, source="TASK_COMPLETION", reference_id=task.id))

    # Run AI Review Analysis with fallback
    prompt_content = f"""
Daily Review Reflection:
- Energy: {review_in.energy_rating}/5
- What went well: {review_in.completed_notes or 'Not specified'}
- Missed tasks reasons: {review_in.missed_reasons or 'None'}
- Tomorrow priorities: {review_in.tomorrow_priorities or 'None'}
"""
    ai_summary = await ollama_client.generate(
        prompt=prompt_content,
        system_prompt=REVIEW_ANALYSIS_SYSTEM_PROMPT,
    )
    if not ai_summary:
        ai_summary = (
            f"Review logged successfully. Energy rating: {review_in.energy_rating}/5. "
            f"Key focus for tomorrow: '{review_in.tomorrow_priorities or 'Follow schedule'}'. "
            "Good job reflecting on today's execution!"
        )

    # Check if review already exists for today, update if so
    review = (
        db.query(DailyReview)
        .filter(DailyReview.user_id == user.id, DailyReview.review_date == target_date)
        .first()
    )
    if not review:
        review = DailyReview(
            user_id=user.id,
            review_date=target_date,
            energy_rating=review_in.energy_rating,
            completed_notes=review_in.completed_notes,
            missed_reasons=review_in.missed_reasons,
            tomorrow_priorities=review_in.tomorrow_priorities,
            deadline_changes=review_in.deadline_changes,
            ai_analysis_summary=ai_summary,
            xp_awarded=50,
        )
        db.add(review)
        user.total_xp += 50
        user.current_level = 10 + (user.total_xp // 100)
        db.add(XPTransaction(user_id=user.id, amount=50, source="DAILY_REVIEW"))
    else:
        review.energy_rating = review_in.energy_rating
        review.completed_notes = review_in.completed_notes
        review.missed_reasons = review_in.missed_reasons
        review.tomorrow_priorities = review_in.tomorrow_priorities
        review.deadline_changes = review_in.deadline_changes
        review.ai_analysis_summary = ai_summary

    db.commit()
    db.refresh(review)
    return review
