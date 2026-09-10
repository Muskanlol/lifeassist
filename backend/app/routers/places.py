from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import PlacesResponse
from app.services.overpass import EXPLORE_CATEGORIES
from app.services.places import nearby_places

router = APIRouter(prefix="/places", tags=["places"])

ALLOWED = {"park", "restaurant", *EXPLORE_CATEGORIES}


@router.get("/nearby", response_model=PlacesResponse)
async def nearby(
    lat: float = Query(...),
    lng: float = Query(...),
    category: str = Query("gym"),
    radius: int = Query(2000, ge=400, le=5000),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    if category not in ALLOWED:
        raise HTTPException(status_code=400, detail="Unknown place category")
    try:
        return await nearby_places(db, category, lat, lng, radius)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not load places: {exc}") from exc
