from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models import CacheMeta
from app.services.geo import grid_key


def geocode_fresh(row) -> bool:
    if not row:
        return False
    return datetime.utcnow() - row.fetched_at < timedelta(hours=settings.cache_ttl_geocode_hours)


def places_fresh(db: Session, category: str, lat: float, lng: float, radius: int) -> bool:
    key = grid_key(category, lat, lng, radius)
    row = db.query(CacheMeta).filter(CacheMeta.grid_key == key).one_or_none()
    if not row:
        return False
    return datetime.utcnow() - row.fetched_at < timedelta(hours=settings.cache_ttl_places_hours)


def walk_fresh(row) -> bool:
    if not row:
        return False
    return datetime.utcnow() - row.fetched_at < timedelta(hours=settings.cache_ttl_walk_hours)
