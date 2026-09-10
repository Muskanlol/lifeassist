from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import LocationOut
from app.services.geocode import resolve_query, suggest_query

router = APIRouter(prefix="/location", tags=["location"])


@router.get("/resolve", response_model=LocationOut)
async def resolve(query: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    try:
        return await resolve_query(db, query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=502, detail="Geocoding is temporarily unavailable")


@router.get("/suggest")
async def suggest(query: str = "", db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return {"suggestions": await suggest_query(db, query)}
