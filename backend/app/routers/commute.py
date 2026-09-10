from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import CrowdIn, CrowdSummaryOut, NearestStopOut, PeakInfoOut
from app.services.commute import nearest_stop, peak_info
from app.services.crowd import add_crowd_report, crowd_summary

router = APIRouter(prefix="/commute", tags=["commute"])


@router.get("/nearest-stop", response_model=NearestStopOut)
async def nearest(
    lat: float = Query(...),
    lng: float = Query(...),
    mode: str = Query("train"),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    if mode not in {"metro", "bus", "train"}:
        raise HTTPException(status_code=400, detail="mode must be metro, bus, or train")
    try:
        return await nearest_stop(db, lat, lng, mode)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not find a nearby stop: {exc}") from exc


@router.get("/peak-info", response_model=PeakInfoOut)
def peaks(
    line: str = Query(...),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return peak_info(db, line)


@router.get("/crowd", response_model=CrowdSummaryOut)
def crowd(
    line: str = Query(...),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return crowd_summary(db, line)


@router.post("/crowd", response_model=CrowdSummaryOut)
def report_crowd(
    body: CrowdIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return add_crowd_report(db, user.id, body.line, body.level, body.stop_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
