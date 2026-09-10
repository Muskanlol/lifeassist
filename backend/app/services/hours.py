from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

DAY_INDEX = {"mo": 0, "tu": 1, "we": 2, "th": 3, "fr": 4, "sa": 5, "su": 6}
TIME_RE = re.compile(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})")
DAY_TOKEN = r"(?:Mo|Tu|We|Th|Fr|Sa|Su)"
DAYS_RE = re.compile(rf"^((?:{DAY_TOKEN})(?:\s*-\s*{DAY_TOKEN})?(?:\s*,\s*{DAY_TOKEN}(?:\s*-\s*{DAY_TOKEN})?)*)\s+(.+)$", re.I)


def _to_minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def _fmt(minutes: int) -> str:
    minutes = minutes % (24 * 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _day_set(spec: str) -> set[int]:
    days: set[int] = set()
    for part in spec.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_raw, end_raw = [bit.strip()[:2].lower() for bit in token.split("-", 1)]
            if start_raw not in DAY_INDEX or end_raw not in DAY_INDEX:
                continue
            start, end = DAY_INDEX[start_raw], DAY_INDEX[end_raw]
            if start <= end:
                days.update(range(start, end + 1))
            else:
                days.update(list(range(start, 7)) + list(range(0, end + 1)))
        else:
            key = token[:2].lower()
            if key in DAY_INDEX:
                days.add(DAY_INDEX[key])
    return days


def _time_ranges(text: str) -> list[tuple[int, int]]:
    ranges = []
    for start, end in TIME_RE.findall(text):
        start_m, end_m = _to_minutes(start), _to_minutes(end)
        ranges.append((start_m, end_m))
    return ranges


def _in_range(now_m: int, start_m: int, end_m: int) -> bool:
    if end_m == start_m:
        return True
    if end_m > start_m:
        return start_m <= now_m < end_m
    return now_m >= start_m or now_m < end_m


def describe_hours(spec: str | None, now: datetime | None = None) -> dict:
    now = now or datetime.now(IST)
    raw = (spec or "").strip()
    if not raw:
        return {"is_open": None, "hours_label": "Hours unknown", "opening_hours": None}

    lowered = raw.lower()
    if lowered in {"24/7", "24 hours", "open 24 hours"}:
        return {"is_open": True, "hours_label": "Open now · 24/7", "opening_hours": raw}

    weekday = now.weekday()
    now_m = now.hour * 60 + now.minute
    today_ranges: list[tuple[int, int]] = []
    closed_today = False

    for chunk in raw.split(";"):
        rule = chunk.strip()
        if not rule or rule.lower().startswith("ph"):
            continue
        match = DAYS_RE.match(rule)
        if match:
            days = _day_set(match.group(1))
            rest = match.group(2).strip()
        else:
            days = set(range(7))
            rest = rule
        if weekday not in days:
            continue
        if rest.lower() in {"off", "closed"}:
            closed_today = True
            today_ranges = []
            continue
        today_ranges.extend(_time_ranges(rest))

    if not today_ranges:
        if closed_today:
            return {"is_open": False, "hours_label": "Closed today", "opening_hours": raw}
        return {"is_open": None, "hours_label": "Hours unknown", "opening_hours": raw}

    for start_m, end_m in today_ranges:
        if _in_range(now_m, start_m, end_m):
            until = _fmt(end_m)
            return {"is_open": True, "hours_label": f"Open now · until {until}", "opening_hours": raw}

    later = sorted(start for start, _ in today_ranges if start > now_m)
    if later:
        return {"is_open": False, "hours_label": f"Opens at {_fmt(later[0])}", "opening_hours": raw}
    return {"is_open": False, "hours_label": "Closed now", "opening_hours": raw}
