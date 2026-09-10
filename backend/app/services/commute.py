from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models import PeakHoursRule
from app.services.places import nearby_places, walking_distance

IST = ZoneInfo("Asia/Kolkata")  # Windows needs the tzdata package

LINE_HINTS = [
    ("western", "Western Line"),
    ("churchgate", "Western Line"),
    ("virar", "Western Line"),
    ("borivali", "Western Line"),
    ("bandra", "Western Line"),
    ("mira road", "Western Line"),
    ("mira-bhayandar", "Western Line"),
    ("harbour", "Harbour Line"),
    ("panvel", "Harbour Line"),
    ("central", "Central Line"),
    ("kasara", "Central Line"),
    ("kalyan", "Central Line"),
    ("metro line 1", "Mumbai Metro Line 1"),
    ("ghatkopar", "Mumbai Metro Line 1"),
    ("versova", "Mumbai Metro Line 1"),
    ("metro line 2", "Mumbai Metro Line 2A"),
    ("metro line 3", "Mumbai Metro Line 3"),
    ("aqua line", "Mumbai Metro Line 3"),
    ("metro line 7", "Mumbai Metro Line 7"),
    ("delhi metro", "Delhi Metro"),
    ("namma", "Namma Metro"),
    ("bengaluru metro", "Namma Metro"),
    ("bangalore metro", "Namma Metro"),
    ("hyderabad metro", "Hyderabad Metro"),
    ("chennai metro", "Chennai Metro"),
    ("kolkata metro", "Kolkata Metro"),
    ("pune metro", "Pune Metro"),
    ("ahmedabad metro", "Ahmedabad Metro"),
    ("lucknow metro", "Lucknow Metro"),
    ("jaipur metro", "Jaipur Metro"),
    ("kochi metro", "Kochi Metro"),
    ("rapid metro", "Rapid Metro Gurgaon"),
]


def guess_line(name: str, extra: str | None, tags: dict | None = None) -> str:
    blob = " ".join(
        part
        for part in [
            name,
            extra or "",
            (tags or {}).get("network", ""),
            (tags or {}).get("operator", ""),
            (tags or {}).get("line", ""),
        ]
        if part
    ).lower()
    for needle, line in LINE_HINTS:
        if needle in blob:
            return line
    if "metro" in blob:
        return "Indian Metro"
    if "bus" in blob:
        return "City Bus"
    return "Suburban Railway"


def current_day_type(now: datetime | None = None) -> str:
    now = now or datetime.now(IST)
    return "weekend" if now.weekday() >= 5 else "weekday"


def _parse_hhmm(value: str):
    hour, minute = value.split(":")
    return int(hour), int(minute)


def is_in_window(now: datetime, start: str, end: str) -> bool:
    sh, sm = _parse_hhmm(start)
    eh, em = _parse_hhmm(end)
    minutes = now.hour * 60 + now.minute
    return sh * 60 + sm <= minutes <= eh * 60 + em


def build_suggestion(now: datetime, windows: list[PeakHoursRule], line: str) -> tuple[bool, str]:
    active = [w for w in windows if is_in_window(now, w.start_time, w.end_time)]
    if active:
        soonest_end = min(active, key=lambda w: _parse_hhmm(w.end_time))
        return True, (
            f"Peak crowding on {line} right now. If you can wait, leave after {soonest_end.end_time}."
        )

    upcoming = []
    now_mins = now.hour * 60 + now.minute
    for window in windows:
        start_mins = _parse_hhmm(window.start_time)[0] * 60 + _parse_hhmm(window.start_time)[1]
        delta = start_mins - now_mins
        if 0 < delta <= 45:
            upcoming.append((delta, window))
    if upcoming:
        _, window = min(upcoming, key=lambda item: item[0])
        return False, (
            f"Off-peak for now, but {line} typically fills up from {window.start_time}. Leave in the next few minutes or after {window.end_time}."
        )
    return False, f"Off-peak on {line}. This is a comfortable time to leave."


def peak_info(db: Session, line: str) -> dict:
    now = datetime.now(IST)
    day_type = current_day_type(now)
    windows = (
        db.query(PeakHoursRule)
        .filter(PeakHoursRule.line_name == line, PeakHoursRule.day_type == day_type)
        .order_by(PeakHoursRule.start_time)
        .all()
    )
    if not windows:
        windows = (
            db.query(PeakHoursRule)
            .filter(PeakHoursRule.line_name == "Indian Metro", PeakHoursRule.day_type == day_type)
            .order_by(PeakHoursRule.start_time)
            .all()
        )
        if windows:
            line = "Indian Metro"
    in_peak, suggestion = build_suggestion(now, windows, line)
    return {
        "line": line,
        "day_type": day_type,
        "now_ist": now.strftime("%H:%M"),
        "in_peak": in_peak,
        "suggestion": suggestion,
        "windows": [
            {
                "line_name": w.line_name,
                "day_type": w.day_type,
                "start_time": w.start_time,
                "end_time": w.end_time,
                "note": w.note,
            }
            for w in windows
        ],
    }


async def nearest_stop(db: Session, lat: float, lng: float, mode: str) -> dict:
    radius = 2500 if mode == "bus" else 4000
    payload = await nearby_places(db, f"transit_{mode}", lat, lng, radius, limit=20)
    matches = payload["places"]
    if not matches:
        raise ValueError("No transit stops found nearby")
    stop = matches[0]
    walk = await walking_distance(db, lat, lng, stop["lat"], stop["lng"])
    line = guess_line(stop["name"], stop.get("extra"))
    return {
        "name": stop["name"],
        "mode": mode,
        "lat": stop["lat"],
        "lng": stop["lng"],
        "distance_m": walk["distance_m"],
        "walk_minutes": walk["walk_minutes"],
        "line_guess": line,
        "extra": stop.get("extra"),
        "cached": payload["cached"],
    }
