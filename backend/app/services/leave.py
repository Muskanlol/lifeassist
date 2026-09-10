from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def parse_hhmm(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def fmt_minutes(total: int) -> str:
    total = max(0, total) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def build_leave_plan(
    *,
    now: datetime,
    line: str,
    walk_minutes: int,
    home_stop: str,
    office_stop: str | None,
    windows: list[dict],
    in_peak: bool,
) -> dict:
    now_m = now.hour * 60 + now.minute
    walk = max(1, int(walk_minutes or 1))
    buffer = 8
    office_bit = f" Alight at {office_stop}." if office_stop else ""

    if in_peak:
        active = [w for w in windows if parse_hhmm(w["start_time"]) <= now_m <= parse_hhmm(w["end_time"])]
        end = min((parse_hhmm(w["end_time"]) for w in active), default=now_m)
        leave_at = fmt_minutes(end)
        return {
            "action": "wait",
            "leave_home_at": leave_at,
            "walk_minutes": walk,
            "home_stop": home_stop,
            "office_stop": office_stop,
            "line": line,
            "headline": (
                f"Peak on {line} until {leave_at}. {walk} min walk to {home_stop}. "
                f"Leave home after {leave_at} unless you want a packed ride.{office_bit}"
            ),
        }

    upcoming = []
    for window in windows:
        start_m = parse_hhmm(window["start_time"])
        if start_m > now_m:
            upcoming.append((start_m, window))
    if upcoming:
        start_m, window = min(upcoming, key=lambda item: item[0])
        leave_m = start_m - walk - buffer
        if leave_m <= now_m:
            return {
                "action": "go_now",
                "leave_home_at": fmt_minutes(now_m),
                "walk_minutes": walk,
                "home_stop": home_stop,
                "office_stop": office_stop,
                "line": line,
                "headline": (
                    f"{line} typically fills from {window['start_time']}. Leave now — "
                    f"{walk} min walk to {home_stop}.{office_bit}"
                ),
            }
        leave_at = fmt_minutes(leave_m)
        return {
            "action": "leave_by",
            "leave_home_at": leave_at,
            "walk_minutes": walk,
            "home_stop": home_stop,
            "office_stop": office_stop,
            "line": line,
            "headline": (
                f"Leave home by {leave_at} to reach {home_stop} before the "
                f"{window['start_time']} crush on {line}.{office_bit}"
            ),
        }

    return {
        "action": "go_now",
        "leave_home_at": fmt_minutes(now_m),
        "walk_minutes": walk,
        "home_stop": home_stop,
        "office_stop": office_stop,
        "line": line,
        "headline": (
            f"Off-peak on {line}. {walk} min walk to {home_stop}. Comfortable time to leave.{office_bit}"
        ),
    }
