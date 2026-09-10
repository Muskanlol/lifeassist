from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import CrowdIn, CrowdSummaryOut, DayPlanOut
from app.services.crowd import add_crowd_report, crowd_summary
from app.services.plan import build_day_plan

router = APIRouter(prefix="/day", tags=["day"])


@router.get("/plan", response_model=DayPlanOut)
async def plan(
    lat: float = Query(...),
    lng: float = Query(...),
    mode: str = Query("train"),
    home: str | None = None,
    office: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if mode not in {"metro", "bus", "train"}:
        raise HTTPException(status_code=400, detail="mode must be metro, bus, or train")
    try:
        return await build_day_plan(
            db,
            lat=lat,
            lng=lng,
            mode=mode,
            home_query=home or user.home_locality,
            office_query=office or user.office_locality,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not build today's plan: {exc}") from exc
