""" Statistics API — 替代前端本地计算 """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core.database import get_db
from ..models.landslide import Landslide

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

@router.get("/by-city")
def by_city(db: Session = Depends(get_db)):
    rows = db.query(Landslide.city, func.count()).filter(Landslide.city != "").group_by(Landslide.city).order_by(func.count().desc()).limit(15).all()
    return [{"name": r[0], "value": r[1]} for r in rows]

@router.get("/by-trigger")
def by_trigger(db: Session = Depends(get_db)):
    rows = db.query(Landslide.trigger, func.count()).filter(Landslide.trigger != "").group_by(Landslide.trigger).order_by(func.count().desc()).all()
    return [{"name": r[0], "value": r[1]} for r in rows]

@router.get("/by-level")
def by_level(db: Session = Depends(get_db)):
    rows = db.query(Landslide.level, func.count()).group_by(Landslide.level).all()
    return [{"name": r[0] or "未知", "value": r[1]} for r in rows]

@router.get("/by-month")
def by_month(db: Session = Depends(get_db)):
    rows = db.query(Landslide.month, func.count()).filter(Landslide.month > 0).group_by(Landslide.month).order_by(Landslide.month).all()
    result = [0] * 12
    for r in rows: result[r[0] - 1] = r[1]
    return result
