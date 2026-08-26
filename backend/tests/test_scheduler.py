import pytest
from datetime import date, datetime, timedelta, timezone
from app.models import Task, FixedSchedule, UserPreferences, DailyReview
from app.services.scheduler_engine import generate_deterministic_schedule
from app.services.conflict_engine import time_to_minutes, intervals_overlap


def test_scheduler_never_overlaps_fixed_schedule():
    fixed = [
        FixedSchedule(id=1, user_id=1, title="Gym", start_time="05:00", end_time="06:30", is_active=True),
        FixedSchedule(id=2, user_id=1, title="Get ready", start_time="06:30", end_time="07:30", is_active=True),
        FixedSchedule(id=3, user_id=1, title="College", start_time="07:30", end_time="12:50", is_active=True),
        FixedSchedule(id=4, user_id=1, title="Lunch", start_time="12:50", end_time="13:15", is_active=True),
    ]

    now = datetime.now(timezone.utc)
    tasks = [
        Task(id=1, title="DSA — Trees", category="DSA", estimated_minutes=90, importance=5, difficulty=4, base_xp=40, deadline=now + timedelta(days=1), status="PENDING"),
        Task(id=2, title="Project — Database", category="Project", estimated_minutes=120, importance=5, difficulty=4, base_xp=50, deadline=now + timedelta(days=2), status="PENDING"),
        Task(id=3, title="Internship Apps", category="Internship", estimated_minutes=60, importance=4, difficulty=3, base_xp=30, deadline=now + timedelta(days=3), status="PENDING"),
        Task(id=4, title="College Assignment", category="College", estimated_minutes=60, importance=3, difficulty=2, base_xp=20, deadline=now + timedelta(days=4), status="PENDING"),
    ]

    pref = UserPreferences(
        user_id=1,
        wake_up_time="05:00",
        sleep_time="22:00",
        max_daily_work_minutes=480,
    )

    plan_result = generate_deterministic_schedule(
        target_date=date.today() + timedelta(days=1),
        fixed_schedules=fixed,
        candidate_tasks=tasks,
        preferences=pref,
    )

    blocks = plan_result.timeline_blocks
    assert len(blocks) > 0

    # Verify no consecutive blocks overlap
    for i in range(len(blocks) - 1):
        curr_b = blocks[i]
        next_b = blocks[i + 1]

        c_start = time_to_minutes(curr_b["start_time"])
        c_end = time_to_minutes(curr_b["end_time"])
        n_start = time_to_minutes(next_b["start_time"])
        n_end = time_to_minutes(next_b["end_time"])

        assert c_end <= n_start, f"Block '{curr_b['title']}' ({curr_b['end_time']}) overlaps with '{next_b['title']}' ({next_b['start_time']})"

    # Verify fixed blocks exist with exact times
    college_block = next((b for b in blocks if b["title"] == "College"), None)
    assert college_block is not None
    assert college_block["start_time"] == "07:30"
    assert college_block["end_time"] == "12:50"


def test_scheduler_postpones_overflow_tasks():
    fixed = [
        FixedSchedule(id=1, user_id=1, title="College All Day", start_time="08:00", end_time="18:00", is_active=True),
    ]

    # Create 10 hours of work tasks
    tasks = [
        Task(id=i, title=f"Giant Task {i}", category="DSA", estimated_minutes=120, importance=3, goal_relevance=3, base_xp=30, status="PENDING")
        for i in range(1, 6)
    ]

    pref = UserPreferences(
        user_id=1,
        wake_up_time="06:00",
        sleep_time="22:00",
        max_daily_work_minutes=240,  # Only 4 hours allowed
    )

    plan_result = generate_deterministic_schedule(
        target_date=date.today() + timedelta(days=1),
        fixed_schedules=fixed,
        candidate_tasks=tasks,
        preferences=pref,
    )

    assert len(plan_result.scheduled_tasks) <= 2
    assert len(plan_result.postponed_tasks) >= 3
    assert plan_result.total_planned_minutes <= 240
