from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.hours import describe_hours
from app.services.leave import build_leave_plan, parse_hhmm


def test_open_now_weekday_lunch():
    now = datetime(2026, 9, 10, 13, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    result = describe_hours("Mo-Fr 11:00-15:00,17:00-23:00", now)
    assert result["is_open"] is True
    assert "until 15:00" in result["hours_label"]


def test_opens_later_today():
    now = datetime(2026, 9, 10, 8, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    result = describe_hours("Mo-Su 11:00-23:00", now)
    assert result["is_open"] is False
    assert result["hours_label"] == "Opens at 11:00"


def test_twenty_four_seven():
    result = describe_hours("24/7")
    assert result["is_open"] is True


def test_unknown_hours():
    result = describe_hours(None)
    assert result["is_open"] is None
    assert result["hours_label"] == "Hours unknown"


def test_leave_by_before_morning_peak():
    now = datetime(2026, 9, 10, 7, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    plan = build_leave_plan(
        now=now,
        line="Western Line",
        walk_minutes=12,
        home_stop="Mira Road",
        office_stop="Bandra",
        windows=[
            {"start_time": "07:30", "end_time": "10:45", "note": ""},
            {"start_time": "17:00", "end_time": "20:30", "note": ""},
        ],
        in_peak=False,
    )
    assert plan["action"] == "leave_by"
    assert plan["leave_home_at"] == "07:10"
    assert "Bandra" in plan["headline"]


def test_wait_during_peak():
    now = datetime(2026, 9, 10, 9, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    plan = build_leave_plan(
        now=now,
        line="Western Line",
        walk_minutes=10,
        home_stop="Borivali",
        office_stop=None,
        windows=[{"start_time": "07:30", "end_time": "10:45", "note": ""}],
        in_peak=True,
    )
    assert plan["action"] == "wait"
    assert plan["leave_home_at"] == "10:45"


def test_parse_hhmm():
    assert parse_hhmm("07:30") == 450


def test_classify_gym_grocery_visit():
    from app.services.overpass import classify_place

    assert classify_place({"leisure": "fitness_centre"}) == "gym"
    assert classify_place({"shop": "supermarket"}) == "grocery"
    assert classify_place({"tourism": "museum"}) == "visit"
    assert classify_place({"amenity": "cinema"}) == "hangout"
    assert classify_place({"shop": "bakery"}) == "specialty"
