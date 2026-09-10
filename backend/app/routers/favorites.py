from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database import get_db
from app.models import Favorite, User
from app.schemas import FavoriteIn, FavoriteOut

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteOut])
def list_favorites(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Favorite).filter(Favorite.user_id == user.id).order_by(Favorite.created_at.desc()).all()


@router.post("", response_model=FavoriteOut)
def add_favorite(body: FavoriteIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.place_key == body.place_key)
        .one_or_none()
    )
    if existing:
        return existing
    row = Favorite(
        user_id=user.id,
        category=body.category,
        name=body.name,
        lat=body.lat,
        lng=body.lng,
        extra=body.extra,
        place_key=body.place_key,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{favorite_id}")
def delete_favorite(favorite_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(Favorite).filter(Favorite.id == favorite_id, Favorite.user_id == user.id).one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(row)
    db.commit()
    return {"ok": True}
