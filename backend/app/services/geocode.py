import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import GeocodeCache, SuggestCache
from app.services.cache import geocode_fresh
from app.services.nominatim import geocode_india, suggest_india

DEMO = {
    "bandra": {
        "query": "Bandra, Mumbai",
        "display_name": "Bandra, Mumbai, Maharashtra, India",
        "lat": 19.0596,
        "lng": 72.8295,
    },
    "borivali": {
        "query": "Borivali, Mumbai",
        "display_name": "Borivali, Mumbai, Maharashtra, India",
        "lat": 19.2307,
        "lng": 72.8567,
    },
    "mira road": {
        "query": "Mira Road, Mumbai",
        "display_name": "Mira Road, Thane, Maharashtra, India",
        "lat": 19.2813,
        "lng": 72.8750,
    },
}

DEMO_SUGGESTIONS = [
    {"query": "Bandra, Mumbai", "display_name": "Bandra, Mumbai, Maharashtra, India", "lat": 19.0596, "lng": 72.8295},
    {"query": "Borivali, Mumbai", "display_name": "Borivali, Mumbai, Maharashtra, India", "lat": 19.2307, "lng": 72.8567},
    {"query": "Mira Road, Mumbai", "display_name": "Mira Road, Thane, Maharashtra, India", "lat": 19.2813, "lng": 72.8750},
]


def _store_geocode(db: Session, key: str, hit: dict) -> None:
    row = db.query(GeocodeCache).filter(GeocodeCache.query == key).one_or_none()
    if row:
        row.display_name = hit["display_name"]
        row.lat = hit["lat"]
        row.lng = hit["lng"]
        row.fetched_at = datetime.utcnow()
    else:
        db.add(
            GeocodeCache(
                query=key,
                display_name=hit["display_name"],
                lat=hit["lat"],
                lng=hit["lng"],
            )
        )
    db.commit()


async def resolve_query(db: Session, query: str) -> dict:
    cleaned = " ".join((query or "").strip().split())
    if not cleaned:
        raise ValueError("Enter a locality name")

    demo = DEMO.get(cleaned.lower())
    if demo:
        return {**demo, "cached": True}

    key = cleaned.lower()
    row = db.query(GeocodeCache).filter(GeocodeCache.query == key).one_or_none()
    if geocode_fresh(row):
        return {
            "query": cleaned,
            "display_name": row.display_name,
            "lat": row.lat,
            "lng": row.lng,
            "cached": True,
        }

    db.rollback()
    try:
        hit = await geocode_india(cleaned if "," in cleaned else f"{cleaned}, India")
    except Exception:
        if row:
            return {
                "query": cleaned,
                "display_name": row.display_name,
                "lat": row.lat,
                "lng": row.lng,
                "cached": True,
            }
        raise

    if not hit:
        raise LookupError("Could not find that locality in India")

    payload = {
        "query": cleaned,
        "display_name": hit["display_name"],
        "lat": hit["lat"],
        "lng": hit["lng"],
        "cached": False,
    }
    _store_geocode(db, key, payload)
    return payload


async def suggest_query(db: Session, query: str) -> list[dict]:
    cleaned = " ".join((query or "").strip().split())
    if len(cleaned) < 2:
        needle = cleaned.lower()
        return [item for item in DEMO_SUGGESTIONS if needle in item["query"].lower()]

    if cleaned.lower() in DEMO or any(cleaned.lower() == item["query"].split(",")[0].lower() for item in DEMO_SUGGESTIONS):
        return DEMO_SUGGESTIONS

    demo_hits = [item for item in DEMO_SUGGESTIONS if cleaned.lower() in item["query"].lower()]
    key = f"suggest:{cleaned.lower()}"
    row = db.query(SuggestCache).filter(SuggestCache.query == key).one_or_none()
    if row and geocode_fresh(row):
        cached = json.loads(row.payload)
        merged = demo_hits + [item for item in cached if item["query"] not in {d["query"] for d in demo_hits}]
        return merged[:6]

    db.rollback()
    try:
        hits = await suggest_india(cleaned)
    except Exception:
        hits = json.loads(row.payload) if row else []

    if row:
        row.payload = json.dumps(hits)
        row.fetched_at = datetime.utcnow()
    else:
        db.add(SuggestCache(query=key, payload=json.dumps(hits)))
    db.commit()
    merged = demo_hits + [item for item in hits if item["query"] not in {d["query"] for d in demo_hits}]
    return merged[:6]
