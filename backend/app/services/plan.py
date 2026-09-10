import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.services.commute import nearest_stop, peak_info
from app.services.crowd import crowd_summary
from app.services.geocode import resolve_query
from app.services.leave import build_leave_plan
from app.services.overpass import EXPLORE_CATEGORIES
from app.services.places import nearby_explore, nearby_places

IST = ZoneInfo("Asia/Kolkata")


def _pick(places: dict, prefer_open: bool = False) -> dict | None:
    items = places.get("places") or []
    if prefer_open:
        opened = [item for item in items if item.get("is_open")]
        if opened:
            return opened[0]
    return items[0] if items else None


def _line(place: dict | None, empty: str) -> str:
    if not place:
        return empty
    detail = place.get("hours_label") or place.get("extra") or place.get("category")
    return f"{place['walk_minutes']} min to {place['name']} · {detail}"


def _morning(parks: dict, food: dict, leave: dict, explore: dict) -> dict:
    park = _pick(parks)
    meal = _pick(food, prefer_open=True)
    gym = _pick(explore.get("gym") or {})
    grocery = _pick(explore.get("grocery") or {})
    hangout = _pick(explore.get("hangout") or {})
    specialty = _pick(explore.get("specialty") or {})
    visit = _pick(explore.get("visit") or {})
    return {
        "run": _line(park, "No mapped park nearby."),
        "eat": _line(meal, "No mapped food spots nearby."),
        "commute": leave["headline"],
        "gym": _line(gym, "No gym mapped nearby."),
        "grocery": _line(grocery, "No grocery mapped nearby."),
        "hangout": _line(hangout, "No hangout spot mapped nearby."),
        "specialty": _line(specialty, "No local specialty mapped nearby."),
        "visit": _line(visit, "No place to visit mapped nearby."),
    }


async def build_day_plan(
    db: Session,
    *,
    lat: float,
    lng: float,
    mode: str,
    home_query: str | None,
    office_query: str | None,
) -> dict:
    empty = {"origin": {"lat": lat, "lng": lng}, "radius_m": 2000, "cached": False, "places": []}
    parks, food = await asyncio.gather(
        nearby_places(db, "park", lat, lng, 2000),
        nearby_places(db, "restaurant", lat, lng, 1500),
        return_exceptions=True,
    )
    if isinstance(parks, Exception):
        parks = {**empty, "radius_m": 2000}
    if isinstance(food, Exception):
        food = {**empty, "radius_m": 1500}
    try:
        explore = await nearby_explore(db, lat, lng, 2000)
    except Exception:
        empty = {"origin": {"lat": lat, "lng": lng}, "radius_m": 2000, "cached": False, "places": []}
        explore = {category: empty for category in EXPLORE_CATEGORIES}

    home_loc = None
    if home_query:
        try:
            home_loc = await resolve_query(db, home_query)
        except Exception:
            home_loc = None
    if not home_loc:
        home_loc = {"query": "Here", "display_name": "Current locality", "lat": lat, "lng": lng, "cached": True}

    office_loc = None
    if office_query:
        try:
            office_loc = await resolve_query(db, office_query)
        except Exception:
            office_loc = None

    try:
        home_stop = await nearest_stop(db, home_loc["lat"], home_loc["lng"], mode)
    except Exception:
        home_stop = {
            "name": "No stop mapped nearby",
            "mode": mode,
            "lat": home_loc["lat"],
            "lng": home_loc["lng"],
            "distance_m": 0,
            "walk_minutes": 8,
            "line_guess": "Suburban Railway",
            "extra": None,
            "cached": False,
        }
    office_stop = None
    if office_loc:
        try:
            office_stop = await nearest_stop(db, office_loc["lat"], office_loc["lng"], mode)
        except Exception:
            office_stop = None

    peak = peak_info(db, home_stop["line_guess"])
    leave = build_leave_plan(
        now=datetime.now(IST),
        line=peak["line"],
        walk_minutes=home_stop["walk_minutes"],
        home_stop=home_stop["name"],
        office_stop=office_stop["name"] if office_stop else None,
        windows=peak["windows"],
        in_peak=peak["in_peak"],
    )
    crowd = crowd_summary(db, peak["line"])
    morning = _morning(parks, food, leave, explore)

    return {
        "parks": parks,
        "food": food,
        "gym": explore["gym"],
        "grocery": explore["grocery"],
        "hangout": explore["hangout"],
        "specialty": explore["specialty"],
        "visit": explore["visit"],
        "home": home_loc,
        "office": office_loc,
        "home_stop": home_stop,
        "office_stop": office_stop,
        "peak": peak,
        "leave": leave,
        "crowd": crowd,
        "morning": morning,
        "mode": mode,
    }
