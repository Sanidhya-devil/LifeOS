import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models import User, FixedSchedule, Task, DailyPlan, ScheduledBlock

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
    # Seed default user
    db = TestingSessionLocal()
    user = User(username="Hero", current_level=12, total_xp=170)
    db.add(user)
    db.commit()
    db.close()
    yield


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}


def test_create_and_get_fixed_schedule():
    payload = {
        "title": "Gym",
        "start_time": "05:00",
        "end_time": "06:30",
        "days_of_week": "mon,tue,wed,thu,fri,sat,sun",
        "is_active": True,
    }
    res = client.post("/api/fixed-schedule", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Gym"
    assert data["start_time"] == "05:00"
    assert data["end_time"] == "06:30"

    list_res = client.get("/api/fixed-schedule")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 1
    assert items[0]["title"] == "Gym"


def test_fixed_schedule_validation_invalid_time():
    payload = {
        "title": "Invalid Block",
        "start_time": "10:00",
        "end_time": "09:00",
    }
    res = client.post("/api/fixed-schedule", json=payload)
    assert res.status_code == 400


def test_create_and_update_task():
    task_payload = {
        "title": "DSA — Trees",
        "description": "Tree algorithms",
        "category": "DSA",
        "estimated_minutes": 90,
        "importance": 5,
        "difficulty": 4,
        "goal_relevance": 5,
        "base_xp": 40,
    }
    res = client.post("/api/tasks", json=task_payload)
    assert res.status_code == 201
    task_data = res.json()
    assert task_data["id"] is not None
    assert task_data["title"] == "DSA — Trees"

    status_res = client.patch(
        f"/api/tasks/{task_data['id']}/status",
        json={"status": "COMPLETED", "actual_minutes": 85},
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "COMPLETED"


def test_review_summary_and_submit():
    summary_res = client.get("/api/reviews/today")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["current_level"] == 12

    review_payload = {
        "energy_rating": 4,
        "completed_notes": "Completed DSA and Project tasks.",
        "missed_reasons": "None",
        "tomorrow_priorities": "Focus on Internship apps.",
    }
    submit_res = client.post("/api/reviews", json=review_payload)
    assert submit_res.status_code == 201
    review_data = submit_res.json()
    assert review_data["energy_rating"] == 4
    assert review_data["xp_awarded"] == 50


def test_plan_generation_validation_and_approval():
    # 1. Add fixed blocks
    client.post("/api/fixed-schedule", json={"title": "Gym", "start_time": "05:00", "end_time": "06:30"})
    client.post("/api/fixed-schedule", json={"title": "College", "start_time": "07:30", "end_time": "12:50"})

    # 2. Add tasks
    client.post("/api/tasks", json={"title": "DSA — Trees", "estimated_minutes": 90, "importance": 5, "base_xp": 40})
    client.post("/api/tasks", json={"title": "Project Work", "estimated_minutes": 120, "importance": 4, "base_xp": 50})

    # 3. Generate proposed plan
    gen_res = client.post("/api/plans/generate", json={})
    assert gen_res.status_code == 201
    plan_data = gen_res.json()
    assert plan_data["status"] == "DRAFT"
    assert len(plan_data["timeline_blocks"]) > 0

    plan_id = plan_data["plan_id"]

    # 4. Validate edit conflict
    task_block = next(b for b in plan_data["timeline_blocks"] if b["block_type"] == "TASK")
    validate_res = client.post(
        f"/api/plans/{plan_id}/validate-edit",
        json={"block_id": task_block["id"], "new_start_time": "08:00", "new_end_time": "09:00"},
    )
    assert validate_res.status_code == 200
    assert validate_res.json()["has_conflict"] is True
    assert "College" in validate_res.json()["message"]

    # 5. Approve plan
    approve_res = client.post(f"/api/plans/{plan_id}/approve")
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"
