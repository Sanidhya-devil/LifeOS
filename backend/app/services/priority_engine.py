from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.models import Task, DailyReview


class PriorityScoreBreakdown:
    def __init__(
        self,
        task_id: int,
        title: str,
        total_score: float,
        deadline_score: float,
        importance_score: float,
        goal_score: float,
        carryover_bonus: float,
        difficulty_weight: float,
        workload_penalty: float,
    ):
        self.task_id = task_id
        self.title = title
        self.total_score = total_score
        self.deadline_score = deadline_score
        self.importance_score = importance_score
        self.goal_score = goal_score
        self.carryover_bonus = carryover_bonus
        self.difficulty_weight = difficulty_weight
        self.workload_penalty = workload_penalty

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "total_score": round(self.total_score, 2),
            "breakdown": {
                "deadline": round(self.deadline_score, 2),
                "importance": round(self.importance_score, 2),
                "goal_relevance": round(self.goal_score, 2),
                "carryover_bonus": round(self.carryover_bonus, 2),
                "difficulty_weight": round(self.difficulty_weight, 2),
                "workload_penalty": round(self.workload_penalty, 2),
            },
        }


def calculate_task_priority(
    task: Task,
    review: Optional[DailyReview] = None,
    user_energy_rating: int = 3,
) -> PriorityScoreBreakdown:
    """
    Deterministically computes a weighted priority score for a task.

    Score Components:
    1. Deadline Urgency:
       - <= 24h: +100
       - <= 48h: +70
       - <= 5 days: +40
       - > 5 days or no deadline: +10
    2. Importance: scale 1-5 multiplied by 15 (max 75)
    3. Goal Relevance: scale 1-5 multiplied by 10 (max 50)
    4. Carryover Bonus: +25 if status is SKIPPED or POSTPONED from today's review
    5. Difficulty & Energy Alignment: +10 bonus if task difficulty matches energy level
    6. Workload Penalty: minor penalty if duration is huge (> 180 min) to avoid starvation
    """
    now = datetime.now(timezone.utc)

    # 1. Deadline urgency
    deadline_score = 10.0
    if task.deadline:
        deadline_utc = task.deadline
        if deadline_utc.tzinfo is None:
            deadline_utc = deadline_utc.replace(tzinfo=timezone.utc)
        time_diff = (deadline_utc - now).total_seconds() / 3600.0  # in hours
        if time_diff <= 24:
            deadline_score = 100.0
        elif time_diff <= 48:
            deadline_score = 70.0
        elif time_diff <= 120:  # 5 days
            deadline_score = 40.0
        else:
            deadline_score = 15.0

    # 2. Importance (1-5) * 15 => 15 to 75
    importance_score = float((task.importance or 3) * 15)

    # 3. Goal Relevance (1-5) * 10 => 10 to 50
    goal_score = float((task.goal_relevance or 3) * 10)

    # 4. Carryover bonus
    carryover_bonus = 0.0
    if task.status in ["SKIPPED", "POSTPONED", "PARTIAL"]:
        carryover_bonus = 25.0

    # If review mentions the task title in tomorrow_priorities, add extra boost
    if review and review.tomorrow_priorities and task.title.lower() in review.tomorrow_priorities.lower():
        carryover_bonus += 20.0

    # 5. Difficulty alignment with energy
    diff = task.difficulty or 3
    # If user has high energy (>=4) and task is high difficulty (>=4), reward it
    difficulty_weight = 0.0
    if user_energy_rating >= 4 and diff >= 4:
        difficulty_weight = 15.0
    elif user_energy_rating <= 2 and diff <= 2:
        difficulty_weight = 10.0

    # 6. Workload penalty (slight penalty for giant blocks > 120 mins)
    workload_penalty = 0.0
    if task.estimated_minutes > 120:
        workload_penalty = float((task.estimated_minutes - 120) // 30) * 5.0

    total_score = (
        deadline_score
        + importance_score
        + goal_score
        + carryover_bonus
        + difficulty_weight
        - workload_penalty
    )

    return PriorityScoreBreakdown(
        task_id=task.id,
        title=task.title,
        total_score=max(0.0, total_score),
        deadline_score=deadline_score,
        importance_score=importance_score,
        goal_score=goal_score,
        carryover_bonus=carryover_bonus,
        difficulty_weight=difficulty_weight,
        workload_penalty=workload_penalty,
    )


def rank_tasks(
    tasks: List[Task],
    review: Optional[DailyReview] = None,
    user_energy_rating: int = 3,
) -> List[tuple[Task, PriorityScoreBreakdown]]:
    """
    Ranks a list of candidate tasks by deterministic priority score in descending order.
    """
    scored = [
        (task, calculate_task_priority(task, review, user_energy_rating))
        for task in tasks
        if task.status != "COMPLETED" and task.status != "CANCELLED"
    ]
    scored.sort(key=lambda x: x[1].total_score, reverse=True)
    return scored
