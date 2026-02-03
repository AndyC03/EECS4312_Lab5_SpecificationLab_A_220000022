from typing import List, Dict


def suggest_slots(
    events: List[Dict[str, str]],
    meeting_duration: int,
    day: str
) -> List[str]:

    WORK_START = 9 * 60       # 09:00
    WORK_END = 17 * 60        # 17:00
    STEP = 15                # minutes

    # Fixed lunch break
    LUNCH_START = 12 * 60     # 12:00
    LUNCH_END = 13 * 60       # 13:00

    def to_minutes(t: str) -> int:
        h, m = map(int, t.split(":"))
        return h * 60 + m

    def to_time_str(minutes: int) -> str:
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    def overlaps(s1, e1, s2, e2) -> bool:
        return s1 < e2 and e1 > s2

    # Convert and filter events to working hours only
    busy_intervals = []
    for event in events:
        start = to_minutes(event["start"])
        end = to_minutes(event["end"])

        # Ignore events completely outside working hours
        if end <= WORK_START or start >= WORK_END:
            continue

        busy_intervals.append((
            max(start, WORK_START),
            min(end, WORK_END)
        ))

    # Add lunch break as a blocked interval
    busy_intervals.append((LUNCH_START, LUNCH_END))

    valid_slots = []
    current = WORK_START

    while current + meeting_duration <= WORK_END:
        meeting_end = current + meeting_duration

        conflict = False
        for b_start, b_end in busy_intervals:
            if overlaps(current, meeting_end, b_start, b_end):
                conflict = True
                break

        if not conflict:
            valid_slots.append(to_time_str(current))

        current += STEP

    return valid_slots
