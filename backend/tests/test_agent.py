import pytest
from datetime import date, datetime, timedelta, timezone
from app.models import Task, FixedSchedule, UserPreferences, DailyReview
from app.agents import planner_agent_app, PlanState, ollama_client


@pytest.mark.asyncio
async def test_ollama_client_fallback_when_offline():
    # Ollama is offline or unmocked, generate should return None without raising exception
    res = await ollama_client.generate("Test prompt")
    assert res is None or isinstance(res, str)


@pytest.mark.asyncio
async def test_langgraph_planner_agent_workflow():
    now = datetime.now(timezone.utc)
    fixed = [
        FixedSchedule(id=1, user_id=1, title="Gym", start_time="05:00", end_time="06:30", is_active=True),
        FixedSchedule(id=2, user_id=1, title="College", start_time="07:30", end_time="12:50", is_active=True),
    ]
    tasks = [
        Task(id=1, user_id=1, title="DSA — Trees", category="DSA", estimated_minutes=90, importance=5, difficulty=4, base_xp=40, deadline=now + timedelta(days=1), status="PENDING"),
        Task(id=2, user_id=1, title="Project — Database", category="Project", estimated_minutes=120, importance=5, difficulty=4, base_xp=50, deadline=now + timedelta(days=2), status="PENDING"),
    ]
    pref = UserPreferences(user_id=1, wake_up_time="05:00", sleep_time="22:00", max_daily_work_minutes=480)
    review = DailyReview(user_id=1, energy_rating=4, completed_notes="Completed assignments", tomorrow_priorities="Focus on DSA Trees")

    state: PlanState = {
        "target_date": date.today() + timedelta(days=1),
        "user_id": 1,
        "strategy": "balanced",
        "fixed_schedules": fixed,
        "candidate_tasks": tasks,
        "preferences": pref,
        "review": review,
        "plan_result": None,
        "review_analysis": None,
        "plan_explanation": None,
        "is_ai_powered": False,
    }

    result_state = await planner_agent_app.ainvoke(state)

    assert result_state["plan_result"] is not None
    assert len(result_state["plan_result"].timeline_blocks) > 0
    assert result_state["plan_explanation"] is not None
    assert "DSA — Trees" in result_state["plan_explanation"] or len(result_state["plan_result"].scheduled_tasks) > 0
    assert result_state["review_analysis"] is not None
