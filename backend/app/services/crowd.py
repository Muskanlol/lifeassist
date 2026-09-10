from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import CrowdReport

LEVELS = {"packed", "ok", "empty"}


def crowd_summary(db: Session, line: str) -> dict:
    since = datetime.utcnow() - timedelta(hours=3)
    rows = (
        db.query(CrowdReport)
        .filter(CrowdReport.line_name == line, CrowdReport.created_at >= since)
        .order_by(CrowdReport.created_at.desc())
        .all()
    )
    counts = {"packed": 0, "ok": 0, "empty": 0}
    for row in rows:
        if row.level in counts:
            counts[row.level] += 1
    latest = rows[0].level if rows else None
    if counts["packed"] >= counts["ok"] and counts["packed"] >= counts["empty"] and counts["packed"]:
        mood = "packed"
    elif counts["empty"] > counts["packed"] and counts["empty"] >= counts["ok"] and counts["empty"]:
        mood = "empty"
    elif rows:
        mood = "ok"
    else:
        mood = None
    return {
        "line": line,
        "mood": mood,
        "latest": latest,
        "counts": counts,
        "reports": len(rows),
        "window_hours": 3,
    }


def add_crowd_report(db: Session, user_id: int, line: str, level: str, stop_name: str | None) -> dict:
    if level not in LEVELS:
        raise ValueError("level must be packed, ok, or empty")
    since = datetime.utcnow() - timedelta(minutes=90)
    existing = (
        db.query(CrowdReport)
        .filter(
            CrowdReport.user_id == user_id,
            CrowdReport.line_name == line,
            CrowdReport.created_at >= since,
        )
        .first()
    )
    if existing:
        existing.level = level
        existing.stop_name = stop_name
        existing.created_at = datetime.utcnow()
        db.add(existing)
    else:
        db.add(
            CrowdReport(
                user_id=user_id,
                line_name=line,
                stop_name=stop_name,
                level=level,
            )
        )
    db.commit()
    return crowd_summary(db, line)
