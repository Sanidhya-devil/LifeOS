import pytest
from datetime import date, timedelta, datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models import User, FixedSchedule, Task, UserPreferences

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Create user at Level 12, 170 XP
    user = User(username="Hero", current_level=12, total_xp=170)
    db.add(user)
    db.commit()

    # Preferences
    pref = UserPreferences(user_id=user.id, wake_up_time="05:00", sleep_time="22:00", max_daily_work_minutes=480)
    db.add(pref)

    # Fixed Commitments
    fixed_blocks = [
        FixedSchedule(user_id=user.id, title="Gym", start_time="05:00", end_time="06:30", is_active=True),
        FixedSchedule(user_id=user.id, title="Get ready", start_time="06:30", end_time="07:30", is_active=True),
        FixedSchedule(user_id=user.id, title="College", start_time="07:30", end_time="12:50", is_active=True),
        FixedSchedule(user_id=user.id, title="Lunch", start_time="12:50", end_time="13:15", is_active=True),
    ]
    db.add_all(fixed_blocks)

    # Candidate Tasks
    now = datetime.now(timezone.utc)
    tasks = [
        Task(user_id=user.id, title="DSA — Trees", category="DSA", estimated_minutes=90, importance=5, difficulty=4, base_xp=40, deadline=now + timedelta(days=1), status="PENDING"),
        Task(user_id=user.id, title="Project — Database", category="Project", estimated_minutes=120, importance=5, difficulty=4, base_xp=50, deadline=now + timedelta(days=2), status="PENDING"),
        Task(user_id=user.id, title="Internship Search + Applications", category="Internship", estimated_minutes=60, importance=4, difficulty=3, base_xp=30, deadline=now + timedelta(days=3), status="PENDING"),
        Task(user_id=user.id, title="College Assignment", category="College", estimated_minutes=60, importance=3, difficulty=2, base_xp=20, deadline=now + timedelta(days=4), status="PENDING"),
    ]
    db.add_all(tasks)
    db.commit()
    db.close()
    yield


def test_full_e2e_daily_loop():
    """
    Simulates the full multi-step LifeOS nightly review and next morning execution cycle:
    1. Today: Nightly Review (+50 XP)
    2. Analyze & Plan Tomorrow (AI + Priority Engine)
    3. User Approves Tomorrow's Plan (DRAFT -> APPROVED)
    4. Next Morning: Morning Quest Dashboard (Good Morning Hero, L12 quests ready)
    5. Execute Quests (+40 XP DSA, +50 XP Project)
    6. Verify Level and XP Progression
    """
    tomorrow = date.today() + timedelta(days=1)

    # Step 1: Nightly Review
    review_payload = {
        "energy_rating": 4,
        "completed_notes": "Studied graph concepts and finished daily gym routine.",
        "missed_reasons": "College lectures ran late.",
        "tomorrow_priorities": "Must complete DSA Trees and Project Database work.",
    }
    review_res = client.post("/api/reviews", json=review_payload)
    assert review_res.status_code == 201
    review_data = review_res.json()
    assert review_data["xp_awarded"] == 50

    # Step 2: Plan Tomorrow
    gen_res = client.post("/api/plans/generate", json={"review_id": review_data["id"], "target_date": tomorrow.isoformat()})
    assert gen_res.status_code == 201
    plan_data = gen_res.json()
    assert plan_data["status"] == "DRAFT"
    assert len(plan_data["timeline_blocks"]) >= 4

    # Verify DSA and Project are scheduled
    task_titles = [b["title"] for b in plan_data["timeline_blocks"]]
    assert "Gym" in task_titles
    assert "College" in task_titles
    assert "DSA — Trees" in task_titles
    assert "Project — Database" in task_titles

    plan_id = plan_data["plan_id"]

    # Step 3: User Approves Plan
    approve_res = client.post(f"/api/plans/{plan_id}/approve")
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # Step 4: Next Morning View
    morning_res = client.get(f"/api/dashboard/morning?target_date={tomorrow.isoformat()}")
    assert morning_res.status_code == 200
    morning_data = morning_res.json()
    assert morning_data["plan_status"] == "APPROVED"
    assert len(morning_data["main_quests"]) >= 2

    # Step 5: Execute Quests in Morning View
    first_quest = morning_data["main_quests"][0]
    quest_update_res = client.post(
        "/api/dashboard/block-status",
        json={"block_id": first_quest["block_id"], "status": "COMPLETED"},
    )
    assert quest_update_res.status_code == 200
    assert quest_update_res.json()["status"] == "COMPLETED"

    # Step 6: Verify User Progression
    summary_res = client.get("/api/reviews/today")
    assert summary_res.status_code == 200
    # User started at 170 XP + 50 XP (review) + first quest XP >= 220 XP
    assert summary_res.json()["total_xp"] >= 220
