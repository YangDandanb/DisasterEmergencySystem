""" Landslide REST API """
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from ..core.database import get_db
from ..models.landslide import Landslide
from ..schemas.landslide import LandslideOut, LandslideCreate, LandslideUpdate

router = APIRouter(prefix="/api/landslides", tags=["landslides"])

@router.get("/export")
def export_geojson(db: Session = Depends(get_db)):
    """ Export all landslides as GeoJSON FeatureCollection """
    rows = db.query(Landslide).all()
    features = []
    for r in rows:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r.lon, r.lat]},
            "properties": {
                "id": r.id, "year": r.year, "month": r.month, "day": r.day,
                "province": r.province, "city": r.city, "county": r.county,
                "town": r.town, "trigger": r.trigger,
                "deaths": r.deaths or 0, "injuries": r.injuries or 0, "missing": r.missing or 0,
                "level": r.level, "level_full": r.level_full,
            }
        })
    return {"type": "FeatureCollection", "features": features}

@router.get("", response_model=list[LandslideOut])
def list_landslides(
    level: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    trigger: Optional[str] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Landslide)
    if level: q = q.filter(Landslide.level == level)
    if city: q = q.filter(Landslide.city == city)
    if trigger: q = q.filter(Landslide.trigger == trigger)
    if year_from: q = q.filter(Landslide.year >= year_from)
    if year_to: q = q.filter(Landslide.year <= year_to)
    return q.limit(limit).all()

@router.post("", response_model=LandslideOut, status_code=201)
def create_landslide(data: LandslideCreate, db: Session = Depends(get_db)):
    point = Point(data.lon, data.lat)
    item = Landslide(
        year=data.year, month=data.month, day=data.day,
        province=data.province, city=data.city, county=data.county, town=data.town,
        trigger=data.trigger, deaths=data.deaths, injuries=data.injuries, missing=data.missing,
        level=data.level, level_full=data.level_full,
        geometry=from_shape(point, srid=4326),
    )
    db.add(item); db.commit(); db.refresh(item); return item

@router.put("/{id}", response_model=LandslideOut)
def update_landslide(id: int, data: LandslideUpdate, db: Session = Depends(get_db)):
    item = db.query(Landslide).filter(Landslide.id == id).first()
    if not item: raise HTTPException(404)
    updates = data.model_dump(exclude_unset=True)
    if 'lon' in updates and 'lat' in updates:
        updates['geometry'] = from_shape(Point(updates.pop('lon'), updates.pop('lat')), srid=4326)
    else:
        updates.pop('lon', None); updates.pop('lat', None)
    for k, v in updates.items(): setattr(item, k, v)
    db.commit(); db.refresh(item); return item

@router.delete("/{id}", status_code=204)
def delete_landslide(id: int, db: Session = Depends(get_db)):
    item = db.query(Landslide).filter(Landslide.id == id).first()
    if not item: raise HTTPException(404)
    db.delete(item); db.commit()
