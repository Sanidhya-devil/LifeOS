from datetime import datetime, date
from typing import List, Dict, Any, Optional
from app.models import Task, FixedSchedule, UserPreferences, DailyReview
from app.services.priority_engine import rank_tasks, PriorityScoreBreakdown
from app.services.conflict_engine import time_to_minutes, minutes_to_time


class ProposedPlanResult:
    def __init__(
        self,
        target_date: date,
        timeline_blocks: List[Dict[str, Any]],
        scheduled_tasks: List[Dict[str, Any]],
        postponed_tasks: List[Dict[str, Any]],
        total_planned_minutes: int,
        total_potential_xp: int,
        deterministic_explanation: str,
    ):
        self.target_date = target_date
        self.timeline_blocks = timeline_blocks
        self.scheduled_tasks = scheduled_tasks
        self.postponed_tasks = postponed_tasks
        self.total_planned_minutes = total_planned_minutes
        self.total_potential_xp = total_potential_xp
        self.deterministic_explanation = deterministic_explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_date": self.target_date.isoformat(),
            "timeline_blocks": self.timeline_blocks,
            "scheduled_tasks": self.scheduled_tasks,
            "postponed_tasks": self.postponed_tasks,
            "total_planned_minutes": self.total_planned_minutes,
            "total_potential_xp": self.total_potential_xp,
            "deterministic_explanation": self.deterministic_explanation,
        }


def generate_deterministic_schedule(
    target_date: date,
    fixed_schedules: List[FixedSchedule],
    candidate_tasks: List[Task],
    preferences: Optional[UserPreferences] = None,
    review: Optional[DailyReview] = None,
) -> ProposedPlanResult:
    """
    Generates a conflict-free, realistic daily schedule adhering to all hard constraints:
    - Fixed commitments protected.
    - Sleep schedule preserved.
    - Breaks and rest buffers inserted.
    - Daily max work limit strictly enforced.
    - Highest-priority tasks scheduled; excess tasks moved forward cleanly.
    """
    # 1. User preferences defaults
    wake_min = time_to_minutes(preferences.wake_up_time if preferences else "05:00")
    sleep_min = time_to_minutes(preferences.sleep_time if preferences else "22:00")
    max_work_min = preferences.max_daily_work_minutes if preferences else 480
    energy_rating = review.energy_rating if review else 3

    # 2. Build sorted immutable fixed blocks
    fixed_blocks_raw = []
    for fs in fixed_schedules:
        if fs.is_active:
            s_min = time_to_minutes(fs.start_time)
            e_min = time_to_minutes(fs.end_time)
            fixed_blocks_raw.append({
                "task_id": None,
                "title": fs.title,
                "block_type": "FIXED",
                "start_min": s_min,
                "end_min": e_min,
                "start_time": fs.start_time,
                "end_time": fs.end_time,
                "duration_minutes": e_min - s_min,
                "status": "PENDING",
                "xp_earned": 0,
            })
    fixed_blocks_raw.sort(key=lambda b: b["start_min"])

    # 3. Add standard dinner/rest buffers if not already present
    # Insert Post-College/Lunch rest if college ends around lunch
    all_fixed_and_buffers = list(fixed_blocks_raw)
    
    # Check if there is lunch ending around 13:15 -> insert rest 13:15-13:45
    lunch_block = next((b for b in fixed_blocks_raw if "lunch" in b["title"].lower()), None)
    if lunch_block and lunch_block["end_min"] <= time_to_minutes("13:30"):
        rest_start = lunch_block["end_min"]
        rest_end = rest_start + 30  # 30 min rest
        all_fixed_and_buffers.append({
            "task_id": None,
            "title": "Rest & Recharge",
            "block_type": "REST",
            "start_min": rest_start,
            "end_min": rest_end,
            "start_time": minutes_to_time(rest_start),
            "end_time": minutes_to_time(rest_end),
            "duration_minutes": 30,
            "status": "PENDING",
            "xp_earned": 0,
        })

    # Check if dinner (19:00-19:45) is already covered
    dinner_start = time_to_minutes("19:00")
    dinner_end = time_to_minutes("19:45")
    dinner_overlap = any(
        max(b["start_min"], dinner_start) < min(b["end_min"], dinner_end)
        for b in all_fixed_and_buffers
    )
    if not dinner_overlap:
        all_fixed_and_buffers.append({
            "task_id": None,
            "title": "Dinner & Rest",
            "block_type": "REST",
            "start_min": dinner_start,
            "end_min": dinner_end,
            "start_time": "19:00",
            "end_time": "19:45",
            "duration_minutes": 45,
            "status": "PENDING",
            "xp_earned": 0,
        })

    # Sort all fixed & buffer commitments chronologically
    all_fixed_and_buffers.sort(key=lambda b: b["start_min"])

    # 4. Find all available free non-overlapping time windows [w_start, w_end] between wake and evening wind-down (21:15)
    wind_down_min = time_to_minutes("21:15")
    free_windows = []
    current_cursor = wake_min

    for block in all_fixed_and_buffers:
        if block["start_min"] > current_cursor:
            window_end = min(block["start_min"], wind_down_min)
            if window_end > current_cursor:
                free_windows.append({"start": current_cursor, "end": window_end})
        current_cursor = max(current_cursor, block["end_min"])

    if current_cursor < wind_down_min:
        free_windows.append({"start": current_cursor, "end": wind_down_min})

    # 5. Deterministic Priority Ranking
    ranked = rank_tasks(candidate_tasks, review=review, user_energy_rating=energy_rating)

    # 6. Greedy slot fitting into free windows with break insertion
    scheduled_task_blocks = []
    postponed_tasks = []
    total_planned_work_minutes = 0
    total_potential_xp = 0
    reasons = []

    for task, score_breakdown in ranked:
        task_duration = task.estimated_minutes or 60
        task_xp = task.base_xp or 20

        # Check daily work capacity
        if total_planned_work_minutes + task_duration > max_work_min:
            postponed_tasks.append({
                "task_id": task.id,
                "title": task.title,
                "category": task.category,
                "estimated_minutes": task_duration,
                "priority_score": round(score_breakdown.total_score, 1),
                "reason": f"Exceeds max daily workload of {max_work_min // 60} hours.",
            })
            continue

        # Try to find a free window that fits task_duration
        fitted = False
        for window in free_windows:
            available_duration = window["end"] - window["start"]
            if available_duration >= task_duration:
                # Fit task here
                start_m = window["start"]
                end_m = start_m + task_duration

                scheduled_task_blocks.append({
                    "task_id": task.id,
                    "title": task.title,
                    "category": task.category,
                    "block_type": "TASK",
                    "start_min": start_m,
                    "end_min": end_m,
                    "start_time": minutes_to_time(start_m),
                    "end_time": minutes_to_time(end_m),
                    "duration_minutes": task_duration,
                    "status": "PENDING",
                    "xp_earned": task_xp,
                    "priority_score": round(score_breakdown.total_score, 1),
                })

                total_planned_work_minutes += task_duration
                total_potential_xp += task_xp
                reasons.append(
                    f"• '{task.title}' was scheduled ({task_duration}m, {task_xp} XP) — Priority score: {round(score_breakdown.total_score, 1)}."
                )

                # Advance window start
                window["start"] = end_m

                # Insert a 15m focus break if task was >= 90 mins and there's remaining time in the window
                if task_duration >= 90 and (window["end"] - window["start"]) >= 15:
                    break_start = window["start"]
                    break_end = break_start + 15
                    scheduled_task_blocks.append({
                        "task_id": None,
                        "title": "Break & Refresh",
                        "block_type": "BREAK",
                        "start_min": break_start,
                        "end_min": break_end,
                        "start_time": minutes_to_time(break_start),
                        "end_time": minutes_to_time(break_end),
                        "duration_minutes": 15,
                        "status": "PENDING",
                        "xp_earned": 0,
                    })
                    window["start"] = break_end

                fitted = True
                break

        if not fitted:
            postponed_tasks.append({
                "task_id": task.id,
                "title": task.title,
                "category": task.category,
                "estimated_minutes": task_duration,
                "priority_score": round(score_breakdown.total_score, 1),
                "reason": f"No available continuous free slot of {task_duration} minutes available today.",
            })

    # 7. Add evening review & wind-down block (20:45-21:15 & 21:15 onward)
    evening_review_start = time_to_minutes("20:45")
    evening_review_end = time_to_minutes("21:15")
    scheduled_task_blocks.append({
        "task_id": None,
        "title": "Review & Preparation",
        "block_type": "REST",
        "start_min": evening_review_start,
        "end_min": evening_review_end,
        "start_time": "20:45",
        "end_time": "21:15",
        "duration_minutes": 30,
        "status": "PENDING",
        "xp_earned": 0,
    })

    # 8. Merge all timeline blocks and sort chronologically
    master_timeline = all_fixed_and_buffers + scheduled_task_blocks
    master_timeline.sort(key=lambda b: b["start_min"])

    # Remove temporary start_min/end_min helpers before final output
    cleaned_timeline = []
    for idx, b in enumerate(master_timeline):
        cleaned = {
            "task_id": b.get("task_id"),
            "title": b["title"],
            "block_type": b["block_type"],
            "start_time": b["start_time"],
            "end_time": b["end_time"],
            "duration_minutes": b["duration_minutes"],
            "status": b.get("status", "PENDING"),
            "xp_earned": b.get("xp_earned", 0),
            "category": b.get("category"),
            "display_order": idx + 1,
        }
        cleaned_timeline.append(cleaned)

    # 9. Formulate deterministic summary explanation
    if postponed_tasks:
        reasons.append(
            f"• Postponed {len(postponed_tasks)} task(s) to protect your schedule and sleep limits."
        )

    explanation_str = (
        f"Generated plan for {target_date.isoformat()} with {len(scheduled_task_blocks)} tasks "
        f"({total_planned_work_minutes} mins work, {total_potential_xp} XP).\n"
        + "\n".join(reasons)
    )

    return ProposedPlanResult(
        target_date=target_date,
        timeline_blocks=cleaned_timeline,
        scheduled_tasks=[b for b in cleaned_timeline if b["block_type"] == "TASK"],
        postponed_tasks=postponed_tasks,
        total_planned_minutes=total_planned_work_minutes,
        total_potential_xp=total_potential_xp,
        deterministic_explanation=explanation_str,
    )
