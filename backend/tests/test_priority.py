import pytest
from datetime import datetime, timedelta, timezone
from app.models import Task, DailyReview
from app.services.priority_engine import calculate_task_priority, rank_tasks


def test_deadline_urgency_scoring():
    now = datetime.now(timezone.utc)
    # Task with deadline within 24h
    urgent_task = Task(
        id=1,
        title="Urgent Assignment",
        importance=3,
        goal_relevance=3,
        estimated_minutes=60,
        deadline=now + timedelta(hours=12),
        status="PENDING",
    )
    # Task with deadline in 4 days
    moderate_task = Task(
        id=2,
        title="Semester Project",
        importance=3,
        goal_relevance=3,
        estimated_minutes=60,
        deadline=now + timedelta(days=4),
        status="PENDING",
    )

    urgent_score = calculate_task_priority(urgent_task)
    moderate_score = calculate_task_priority(moderate_task)

    assert urgent_score.deadline_score == 100.0
    assert moderate_score.deadline_score == 40.0
    assert urgent_score.total_score > moderate_score.total_score


def test_carryover_and_review_priorities_bonus():
    # Carried over / skipped task
    skipped_task = Task(
        id=3,
        title="DSA — Trees",
        importance=4,
        goal_relevance=4,
        estimated_minutes=90,
        status="SKIPPED",
    )
    review = DailyReview(
        user_id=1,
        tomorrow_priorities="Must complete DSA — Trees tomorrow without fail",
    )

    score = calculate_task_priority(skipped_task, review=review)
    # 25 (carryover) + 20 (mentioned in tomorrow_priorities) = 45 bonus
    assert score.carryover_bonus == 45.0


def test_rank_tasks_ordering():
    now = datetime.now(timezone.utc)
    t1 = Task(id=1, title="Low Priority Task", importance=1, goal_relevance=1, estimated_minutes=60, status="PENDING")
    t2 = Task(id=2, title="Urgent High Impact Task", importance=5, goal_relevance=5, estimated_minutes=90, deadline=now + timedelta(hours=18), status="PENDING")
    t3 = Task(id=3, title="Completed Task", importance=5, goal_relevance=5, estimated_minutes=60, status="COMPLETED")

    ranked = rank_tasks([t1, t2, t3])
    assert len(ranked) == 2  # Completed task excluded
    assert ranked[0][0].id == 2  # Urgent high impact task ranked first
    assert ranked[1][0].id == 1
