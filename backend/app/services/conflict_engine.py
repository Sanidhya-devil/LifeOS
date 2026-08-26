from typing import List, Dict, Any, Optional, Tuple


def time_to_minutes(time_str: str) -> int:
    """Converts 'HH:MM' 24-hour time string to minutes from 00:00."""
    parts = time_str.strip().split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    return hours * 60 + minutes


def minutes_to_time(minutes: int) -> str:
    """Converts minutes from 00:00 to 'HH:MM' format."""
    hours = (minutes // 60) % 24
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def intervals_overlap(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    """Returns True if interval [start_a, end_a] overlaps with [start_b, end_b]."""
    return max(start_a, start_b) < min(end_a, end_b)


def detect_edit_conflict(
    blocks: List[Dict[str, Any]],
    target_block_id: int,
    new_start_time: str,
    new_end_time: str,
) -> Dict[str, Any]:
    """
    Detects if modifying target_block_id to [new_start_time, new_end_time] overlaps with
    any other scheduled block or fixed commitment.

    Returns:
        {
            "has_conflict": bool,
            "conflicting_block": Optional[Dict],
            "message": str,
            "suggested_options": List[str]
        }
    """
    new_start = time_to_minutes(new_start_time)
    new_end = time_to_minutes(new_end_time)

    if new_start >= new_end:
        return {
            "has_conflict": True,
            "conflicting_block": None,
            "message": "Start time must be strictly earlier than end time.",
            "suggested_options": ["Adjust end time to be after start time", "Cancel edit"],
        }

    for b in blocks:
        # Don't check against the block itself
        if b.get("id") == target_block_id:
            continue

        b_start = time_to_minutes(b["start_time"])
        b_end = time_to_minutes(b["end_time"])

        if intervals_overlap(new_start, new_end, b_start, b_end):
            conflicting_title = b.get("title", "Existing Block")
            block_type = b.get("block_type", "TASK")
            time_range = f"{b['start_time']}–{b['end_time']}"

            if block_type == "FIXED":
                return {
                    "has_conflict": True,
                    "conflicting_block": b,
                    "message": f"⚠️ Overlaps with non-negotiable fixed commitment: '{conflicting_title}' ({time_range}).",
                    "suggested_options": [
                        f"Move before {b['start_time']}",
                        f"Move after {b['end_time']}",
                        "Cancel edit",
                    ],
                }

            return {
                "has_conflict": True,
                "conflicting_block": b,
                "message": f"⚠️ This creates a conflict with '{conflicting_title}' ({time_range}).",
                "suggested_options": [
                    f"Move '{conflicting_title}' forward",
                    f"Reduce duration to fit before {b['start_time']}",
                    "Cancel edit",
                ],
            }

    return {
        "has_conflict": False,
        "conflicting_block": None,
        "message": "Time slot is free and valid.",
        "suggested_options": [],
    }
