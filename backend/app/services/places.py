import asyncio
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import CacheMeta, CachedPlace, WalkCache
from app.services.cache import places_fresh, walk_fresh
from app.services.geo import grid_key, haversine_m, walk_cache_key, walk_minutes
from app.services.hours import describe_hours
from app.services.osrm import estimate_walk, walking_route
from app.services.overpass import EXPLORE_CATEGORIES, query_overpass

_grid_locks: dict[str, asyncio.Lock] = {}


def _store_places(db: Session, key: str, category: str, places: list[dict]) -> None:
    db.query(CachedPlace).filter(CachedPlace.grid_key == key).delete()
    meta = db.query(CacheMeta).filter(CacheMeta.grid_key == key).one_or_none()
    now = datetime.utcnow()
    if meta:
        meta.fetched_at = now
    else:
        db.add(CacheMeta(grid_key=key, fetched_at=now))
    for place in places:
        db.add(
            CachedPlace(
                category=place.get("category") or category,
                grid_key=key,
                name=place["name"],
                lat=place["lat"],
                lng=place["lng"],
                extra=place.get("extra"),
                raw_tags=json.dumps(place.get("raw_tags") or {}),
                fetched_at=now,
            )
        )
    db.commit()


def _load_places(db: Session, key: str) -> list[dict]:
    rows = db.query(CachedPlace).filter(CachedPlace.grid_key == key).all()
    return [
        {
            "name": row.name or "Unnamed",
            "category": row.category,
            "lat": row.lat,
            "lng": row.lng,
            "extra": row.extra,
            "raw_tags": json.loads(row.raw_tags) if row.raw_tags else {},
        }
        for row in rows
    ]


def _with_distance(origin_lat: float, origin_lng: float, places: list[dict]) -> list[dict]:
    scored = []
    for place in places:
        distance = haversine_m(origin_lat, origin_lng, place["lat"], place["lng"])
        scored.append(
            {
                **place,
                "distance_m": int(round(distance)),
                "walk_minutes": walk_minutes(distance),
            }
        )
    scored.sort(key=lambda item: item["distance_m"])
    return scored


async def nearby_places(
    db: Session,
    category: str,
    lat: float,
    lng: float,
    radius: int,
    limit: int = 20,
) -> dict:
    key = grid_key(category, lat, lng, radius)
    lock = _grid_locks.setdefault(key, asyncio.Lock())
    async with lock:
        cached = places_fresh(db, category, lat, lng, radius)
        if cached:
            places = _load_places(db, key)
            db.rollback()
        else:
            db.rollback()
            try:
                places = await query_overpass(category, lat, lng, radius)
                _store_places(db, key, category, places)
                cached = False
            except Exception:
                places = _load_places(db, key)
                cached = bool(places)
                db.rollback()
                if not places:
                    raise
    ranked = _with_distance(lat, lng, places)
    ranked = [p for p in ranked if p["distance_m"] <= radius + 80][:limit]
    serialized = []
    for place in ranked:
        tags = place.get("raw_tags") or {}
        category = tags.get("amenity") or tags.get("leisure") or place["category"]
        hours = describe_hours(tags.get("opening_hours"))
        serialized.append(
            {
                "name": place["name"],
                "category": category,
                "lat": place["lat"],
                "lng": place["lng"],
                "distance_m": place["distance_m"],
                "walk_minutes": place["walk_minutes"],
                "extra": place.get("extra"),
                "place_key": f"{place['name']}|{place['lat']:.5f}|{place['lng']:.5f}",
                "is_open": hours["is_open"],
                "hours_label": hours["hours_label"],
                "opening_hours": hours["opening_hours"],
            }
        )
    return {
        "origin": {"lat": lat, "lng": lng},
        "radius_m": radius,
        "cached": cached,
        "places": serialized,
    }


def _empty_places(lat: float, lng: float, radius: int) -> dict:
    return {"origin": {"lat": lat, "lng": lng}, "radius_m": radius, "cached": False, "places": []}


async def nearby_explore(db: Session, lat: float, lng: float, radius: int = 2000, limit: int = 20) -> dict:
    bundle_key = grid_key("explore", lat, lng, radius)
    lock = _grid_locks.setdefault(bundle_key, asyncio.Lock())
    async with lock:
        if all(places_fresh(db, category, lat, lng, radius) for category in EXPLORE_CATEGORIES):
            db.rollback()
            return {
                category: await nearby_places(db, category, lat, lng, radius, limit)
                for category in EXPLORE_CATEGORIES
            }

        db.rollback()
        try:
            found = await query_overpass("explore", lat, lng, radius)
        except Exception:
            packed = {}
            for category in EXPLORE_CATEGORIES:
                try:
                    packed[category] = await nearby_places(db, category, lat, lng, radius, limit)
                except Exception:
                    packed[category] = _empty_places(lat, lng, radius)
            if any(item["places"] for item in packed.values()):
                return packed
            raise

        grouped = {category: [] for category in EXPLORE_CATEGORIES}
        for place in found:
            bucket = place.get("category")
            if bucket in grouped:
                grouped[bucket].append(place)
        for category, items in grouped.items():
            _store_places(db, grid_key(category, lat, lng, radius), category, items)
        return {
            category: await nearby_places(db, category, lat, lng, radius, limit)
            for category in EXPLORE_CATEGORIES
        }


async def walking_distance(db: Session, lat1: float, lng1: float, lat2: float, lng2: float) -> dict:
    key = walk_cache_key(lat1, lng1, lat2, lng2)
    row = db.query(WalkCache).filter(WalkCache.cache_key == key).one_or_none()
    if walk_fresh(row):
        return {
            "distance_m": int(round(row.distance_m)),
            "walk_minutes": walk_minutes(row.distance_m),
            "cached": True,
        }
    routed = await walking_route(lat1, lng1, lat2, lng2)
    payload = routed or estimate_walk(lat1, lng1, lat2, lng2)
    minutes = walk_minutes(payload["distance_m"])
    payload["walk_minutes"] = minutes
    payload["duration_s"] = minutes * 60
    if row:
        row.distance_m = payload["distance_m"]
        row.duration_s = payload["duration_s"]
        row.fetched_at = datetime.utcnow()
    else:
        db.add(
            WalkCache(
                cache_key=key,
                distance_m=payload["distance_m"],
                duration_s=payload["duration_s"],
            )
        )
    db.commit()
    return {
        "distance_m": int(round(payload["distance_m"])),
        "walk_minutes": payload["walk_minutes"],
        "cached": False,
    }
