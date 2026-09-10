from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import PlacesResponse
from app.services.places import nearby_places

router = APIRouter(prefix="/parks", tags=["parks"])


@router.get("/nearby", response_model=PlacesResponse)
async def nearby(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: int = Query(2000, ge=400, le=5000),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    try:
        return await nearby_places(db, "park", lat, lng, radius)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not load parks: {exc}") from exc
