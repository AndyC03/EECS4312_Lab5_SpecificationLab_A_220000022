## Student Name: Andy
## Student ID: 220000022

"""
Public test suite for the meeting slot suggestion exercise.

Students can run these tests locally to check basic correctness of their implementation.
The hidden test suite used for grading contains additional edge cases and will not be
available to students.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from src.solution import suggest_slots


def test_single_event_blocks_overlapping_slots():
    """
    Functional requirement:
    Slots overlapping an event must not be suggested.
    """
    events = [{"start": "10:00", "end": "11:00"}]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert "10:00" not in slots
    assert "10:30" not in slots
    assert "11:15" in slots

def test_event_outside_working_hours_is_ignored():
    """
    Constraint:
    Events completely outside working hours should not affect availability.
    """
    events = [{"start": "07:00", "end": "08:00"}]
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-01")

    assert "09:00" in slots
    assert "16:00" in slots

def test_unsorted_events_are_handled():
    """
    Constraint:
    Event order should not affect correctness.
    """
    events = [
        {"start": "13:00", "end": "14:00"},
        {"start": "09:30", "end": "10:00"},
        {"start": "11:00", "end": "12:00"},
    ]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert slots[0] == "09:00"
    assert slots[1] == "10:00"
    assert "10:15" in slots
    assert "09:30" not in slots

def test_lunch_break_blocks_all_slots_during_lunch():
    """
    Constraint:
    No meeting may start during the lunch break (12:00–13:00).
    """
    events = []
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert "12:00" not in slots
    assert "12:15" not in slots
    assert "12:30" not in slots
    assert "12:45" not in slots


def test_friday_no_slots_after_15_00():
    """
    Constraint:
    On Fridays, no meeting may start at or after 15:00.
    """
    # 2026-02-06 is a Friday
    events = []
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-06")
    assert "14:45" in slots
    assert "15:00" not in slots
    assert "15:30" not in slots
    assert "16:00" not in slots


def test_non_friday_afternoon_slots_allowed():
    """
    Constraint:
    On non-Fridays, slots at 15:00 and later are allowed (within working hours).
    """
    # 2026-02-02 is a Monday
    events = []
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-02")
    assert "15:00" in slots
    assert "16:00" in slots
    assert "16:30" in slots


def test_friday_with_events_respects_cutoff():
    """
    On Friday, valid slots before 15:00 are still suggested; after 15:00 none.
    """
    events = [{"start": "10:00", "end": "11:00"}]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-06")  # Friday
    assert "09:00" in slots
    assert "11:30" in slots
    assert "14:45" in slots
    assert "15:00" not in slots
    assert all(to_minutes(s) < 15 * 60 for s in slots), "No Friday slot should start at or after 15:00"


def test_meeting_duration_fits_before_end_of_day():
    """
    Last possible start for a 60-min meeting is 16:00 (ends at 17:00).
    """
    events = []
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-02")
    assert "16:00" in slots
    assert "16:15" not in slots
    assert "16:30" not in slots


def test_event_ending_at_work_start_does_not_block_09_00():
    """
    Event ending exactly at 09:00 should not block the 09:00 slot.
    """
    events = [{"start": "08:00", "end": "09:00"}]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")
    assert "09:00" in slots


def test_event_starting_at_work_end_does_not_block_last_slot():
    """
    Event starting exactly at 17:00 should not block 16:00 for a 60-min meeting.
    """
    events = [{"start": "17:00", "end": "18:00"}]
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-01")
    assert "16:00" in slots


def test_multiple_events_leave_correct_gaps():
    """
    Multiple back-to-back events only allow slots in the gaps.
    """
    events = [
        {"start": "09:00", "end": "10:00"},
        {"start": "10:00", "end": "11:00"},
        {"start": "11:00", "end": "12:00"},
    ]
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-01")
    # Only 13:00-17:00 available for 60-min (after lunch)
    assert "13:00" in slots
    assert "09:00" not in slots
    assert "10:00" not in slots
    assert "11:00" not in slots


def to_minutes(t: str) -> int:
    """Helper to parse "HH:MM" to minutes since midnight."""
    h, m = map(int, t.split(":"))
    return h * 60 + m

