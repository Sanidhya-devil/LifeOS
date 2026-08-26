from typing import TypedDict, List, Dict, Any, Optional
from datetime import date, datetime, timezone
from langgraph.graph import StateGraph, END
from app.models import Task, FixedSchedule, UserPreferences, DailyReview
from app.services import (
    generate_deterministic_schedule,
    ProposedPlanResult,
    rank_tasks,
)
from app.agents.ollama_client import ollama_client
from app.agents.prompts import (
    REVIEW_ANALYSIS_SYSTEM_PROMPT,
    PLAN_EXPLANATION_SYSTEM_PROMPT,
)


class PlanState(TypedDict):
    target_date: date
    user_id: int
    strategy: str
    fixed_schedules: List[FixedSchedule]
    candidate_tasks: List[Task]
    preferences: Optional[UserPreferences]
    review: Optional[DailyReview]
    plan_result: Optional[ProposedPlanResult]
    review_analysis: Optional[str]
    plan_explanation: Optional[str]
    is_ai_powered: bool


async def analyze_review_node(state: PlanState) -> Dict[str, Any]:
    """Node: Analyzes today's review reflections to extract key trends and carryover signals."""
    review = state.get("review")
    if not review:
        return {"review_analysis": "No prior review logged for today.", "is_ai_powered": False}

    user_prompt = f"""
Daily Review Reflection:
- Energy Level: {review.energy_rating}/5
- Completed Notes: {review.completed_notes or 'None'}
- Missed Reasons: {review.missed_reasons or 'None'}
- Tomorrow's Priorities: {review.tomorrow_priorities or 'None'}
- Deadline Changes: {review.deadline_changes or 'None'}
"""
    ai_response = await ollama_client.generate(
        prompt=user_prompt,
        system_prompt=REVIEW_ANALYSIS_SYSTEM_PROMPT,
    )

    if ai_response:
        return {"review_analysis": ai_response, "is_ai_powered": True}
    
    # Deterministic fallback
    fallback_analysis = (
        f"• Energy Rating: {review.energy_rating}/5\n"
        f"• Tomorrow Focus: {review.tomorrow_priorities or 'Follow prioritized quests'}\n"
        f"• Missed Reasons addressed: {review.missed_reasons or 'None'}"
    )
    return {"review_analysis": fallback_analysis, "is_ai_powered": False}


async def schedule_generation_node(state: PlanState) -> Dict[str, Any]:
    """Node: Runs the deterministic priority and slotting engine."""
    target_date = state["target_date"]
    fixed_schedules = state["fixed_schedules"]
    candidate_tasks = state["candidate_tasks"]
    preferences = state.get("preferences")
    review = state.get("review")

    plan_result = generate_deterministic_schedule(
        target_date=target_date,
        fixed_schedules=fixed_schedules,
        candidate_tasks=candidate_tasks,
        preferences=preferences,
        review=review,
    )
    return {"plan_result": plan_result}


async def explain_plan_node(state: PlanState) -> Dict[str, Any]:
    """Node: Generates the natural language 'Why this plan?' reasoning."""
    plan_result: ProposedPlanResult = state["plan_result"]
    review = state.get("review")

    scheduled_titles = [f"{b['title']} ({b['duration_minutes']}m, {b['start_time']}–{b['end_time']})" for b in plan_result.timeline_blocks if b["block_type"] == "TASK"]
    postponed_titles = [f"{p['title']} ({p['estimated_minutes']}m) — Reason: {p['reason']}" for p in plan_result.postponed_tasks]

    user_prompt = f"""
Target Date: {state['target_date'].isoformat()}
Total Planned Work: {plan_result.total_planned_minutes} minutes
Total Potential XP: {plan_result.total_potential_xp} XP

Scheduled Tasks:
{chr(10).join(scheduled_titles) if scheduled_titles else 'None'}

Postponed Tasks (Moved Forward):
{chr(10).join(postponed_titles) if postponed_titles else 'None'}

User Notes / Priorities from Review:
{review.tomorrow_priorities if review and review.tomorrow_priorities else 'None specified'}
"""

    ai_response = await ollama_client.generate(
        prompt=user_prompt,
        system_prompt=PLAN_EXPLANATION_SYSTEM_PROMPT,
    )

    if ai_response:
        return {"plan_explanation": ai_response, "is_ai_powered": True}

    # Deterministic fallback explanation
    return {"plan_explanation": plan_result.deterministic_explanation, "is_ai_powered": False}


def build_planner_workflow() -> StateGraph:
    """Builds the LangGraph state machine for review analysis, scheduling, and explanation."""
    workflow = StateGraph(PlanState)

    # Add Nodes
    workflow.add_node("analyze_review", analyze_review_node)
    workflow.add_node("generate_schedule", schedule_generation_node)
    workflow.add_node("explain_plan", explain_plan_node)

    # Add Edges
    workflow.set_entry_point("analyze_review")
    workflow.add_edge("analyze_review", "generate_schedule")
    workflow.add_edge("generate_schedule", "explain_plan")
    workflow.add_edge("explain_plan", END)

    return workflow.compile()


planner_agent_app = build_planner_workflow()
