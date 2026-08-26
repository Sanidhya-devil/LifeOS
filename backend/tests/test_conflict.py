import pytest
from app.services.conflict_engine import (
    time_to_minutes,
    minutes_to_time,
    intervals_overlap,
    detect_edit_conflict,
)


def test_time_conversions():
    assert time_to_minutes("00:00") == 0
    assert time_to_minutes("05:00") == 300
    assert time_to_minutes("07:30") == 450
    assert time_to_minutes("12:50") == 770
    assert time_to_minutes("23:59") == 1439

    assert minutes_to_time(300) == "05:00"
    assert minutes_to_time(450) == "07:30"
    assert minutes_to_time(770) == "12:50"


def test_interval_overlap():
    # Overlapping intervals
    assert intervals_overlap(100, 200, 150, 250) is True
    assert intervals_overlap(100, 300, 150, 200) is True  # Containment
    assert intervals_overlap(150, 200, 100, 300) is True

    # Non-overlapping intervals (adjacent / disjoint)
    assert intervals_overlap(100, 200, 200, 300) is False
    assert intervals_overlap(100, 150, 200, 300) is False


def test_detect_edit_conflict_with_fixed_schedule():
    blocks = [
        {"id": 1, "title": "Gym", "block_type": "FIXED", "start_time": "05:00", "end_time": "06:30"},
        {"id": 2, "title": "College", "block_type": "FIXED", "start_time": "07:30", "end_time": "12:50"},
        {"id": 3, "title": "DSA — Trees", "block_type": "TASK", "start_time": "13:45", "end_time": "15:15"},
    ]

    # Try to move DSA into college hours (08:00–09:30)
    conflict = detect_edit_conflict(blocks, target_block_id=3, new_start_time="08:00", new_end_time="09:30")
    assert conflict["has_conflict"] is True
    assert "College" in conflict["message"]
    assert "non-negotiable" in conflict["message"]

    # Valid non-overlapping edit (15:30–17:00)
    no_conflict = detect_edit_conflict(blocks, target_block_id=3, new_start_time="15:30", new_end_time="17:00")
    assert no_conflict["has_conflict"] is False
