from datetime import datetime, timedelta, timezone
from app.database import SessionLocal, engine, Base
from app.models import User, UserPreferences, FixedSchedule, Task, DailyPlan, ScheduledBlock

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if user already exists
        user = db.query(User).first()
        if not user:
            user = User(
                username="Hero",
                current_level=12,
                total_xp=170,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created default user: {user.username} (Level {user.current_level}, {user.total_xp} XP)")

        # Seed User Preferences
        pref = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        if not pref:
            pref = UserPreferences(
                user_id=user.id,
                wake_up_time="05:00",
                sleep_time="22:00",
                max_daily_work_minutes=480,
                default_break_minutes=15,
                preferred_focus_block_minutes=90,
                energy_peak_time="morning",
            )
            db.add(pref)
            db.commit()
            print("Seeded user preferences")

        # Seed Initial Fixed Schedule
        fixed_items = [
            {"title": "Gym", "start_time": "05:00", "end_time": "06:30"},
            {"title": "Get ready", "start_time": "06:30", "end_time": "07:30"},
            {"title": "College", "start_time": "07:30", "end_time": "12:50"},
            {"title": "Lunch", "start_time": "12:50", "end_time": "13:15"},
        ]

        existing_fixed = db.query(FixedSchedule).filter(FixedSchedule.user_id == user.id).count()
        if existing_fixed == 0:
            for item in fixed_items:
                fixed_block = FixedSchedule(
                    user_id=user.id,
                    title=item["title"],
                    start_time=item["start_time"],
                    end_time=item["end_time"],
                    days_of_week="mon,tue,wed,thu,fri,sat,sun",
                    is_active=True,
                )
                db.add(fixed_block)
            db.commit()
            print(f"Seeded {len(fixed_items)} fixed schedule commitments")

        # Seed Sample Tasks
        now = datetime.now(timezone.utc)
        sample_tasks = [
            {
                "title": "DSA — Trees",
                "description": "Binary tree traversals and LCA problems",
                "category": "DSA",
                "estimated_minutes": 90,
                "importance": 5,
                "difficulty": 4,
                "goal_relevance": 5,
                "deadline": now + timedelta(days=2),
                "base_xp": 40,
                "status": "PENDING",
            },
            {
                "title": "Project — Database",
                "description": "Design schema and implement SQLAlchemy models with migrations",
                "category": "Project",
                "estimated_minutes": 120,
                "importance": 5,
                "difficulty": 4,
                "goal_relevance": 5,
                "deadline": now + timedelta(days=3),
                "base_xp": 50,
                "status": "PENDING",
            },
            {
                "title": "Internship Search + Applications",
                "description": "Apply to 3 backend / AI engineer internship postings",
                "category": "Internship",
                "estimated_minutes": 60,
                "importance": 4,
                "difficulty": 3,
                "goal_relevance": 4,
                "deadline": now + timedelta(days=4),
                "base_xp": 30,
                "status": "PENDING",
            },
            {
                "title": "College Assignment",
                "description": "Complete Operating Systems memory management problem set",
                "category": "College",
                "estimated_minutes": 60,
                "importance": 3,
                "difficulty": 2,
                "goal_relevance": 3,
                "deadline": now + timedelta(days=5),
                "base_xp": 20,
                "status": "PENDING",
            },
        ]

        existing_tasks = db.query(Task).filter(Task.user_id == user.id).count()
        if existing_tasks == 0:
            for t in sample_tasks:
                task = Task(
                    user_id=user.id,
                    title=t["title"],
                    description=t["description"],
                    category=t["category"],
                    estimated_minutes=t["estimated_minutes"],
                    importance=t["importance"],
                    difficulty=t["difficulty"],
                    goal_relevance=t["goal_relevance"],
                    deadline=t["deadline"],
                    base_xp=t["base_xp"],
                    status=t["status"],
                )
                db.add(task)
            db.commit()
            print(f"Seeded {len(sample_tasks)} initial tasks")

        print("Database seeding completed successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
