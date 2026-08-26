import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import (
    User,
    UserPreferences,
    FixedSchedule,
    Task,
    DailyReview,
    DailyPlan,
    ScheduledBlock,
    XPTransaction,
)

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_user_and_preferences(db_session):
    user = User(username="TestHero", current_level=12, total_xp=170)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    pref = UserPreferences(
        user_id=user.id,
        wake_up_time="05:00",
        sleep_time="22:00",
        max_daily_work_minutes=480,
    )
    db_session.add(pref)
    db_session.commit()

    assert user.id is not None
    assert user.preferences.wake_up_time == "05:00"
    assert user.preferences.max_daily_work_minutes == 480


def test_fixed_schedule_creation(db_session):
    user = User(username="Hero")
    db_session.add(user)
    db_session.commit()

    fixed = FixedSchedule(
        user_id=user.id,
        title="Gym",
        start_time="05:00",
        end_time="06:30",
        is_active=True,
    )
    db_session.add(fixed)
    db_session.commit()

    assert fixed.id is not None
    assert fixed.title == "Gym"
    assert fixed.start_time == "05:00"


def test_task_lifecycle_and_xp(db_session):
    user = User(username="Hero", total_xp=100, current_level=11)
    db_session.add(user)
    db_session.commit()

    task = Task(
        user_id=user.id,
        title="DSA — Trees",
        category="DSA",
        estimated_minutes=90,
        importance=5,
        difficulty=4,
        base_xp=40,
        status="PENDING",
    )
    db_session.add(task)
    db_session.commit()

    assert task.id is not None
    assert task.status == "PENDING"
    assert task.base_xp == 40


def test_daily_plan_and_scheduled_blocks(db_session):
    user = User(username="Hero")
    db_session.add(user)
    db_session.commit()

    plan = DailyPlan(
        user_id=user.id,
        plan_date=date.today(),
        status="DRAFT",
        total_planned_minutes=150,
        total_potential_xp=90,
        ai_reasoning="Prioritized DSA and Project.",
    )
    db_session.add(plan)
    db_session.commit()

    block1 = ScheduledBlock(
        plan_id=plan.id,
        title="Gym",
        block_type="FIXED",
        start_time="05:00",
        end_time="06:30",
        duration_minutes=90,
    )
    block2 = ScheduledBlock(
        plan_id=plan.id,
        title="DSA — Trees",
        block_type="TASK",
        start_time="13:45",
        end_time="15:15",
        duration_minutes=90,
    )
    db_session.add_all([block1, block2])
    db_session.commit()

    assert len(plan.scheduled_blocks) == 2
    assert plan.scheduled_blocks[0].title == "Gym"
    assert plan.scheduled_blocks[1].title == "DSA — Trees"
