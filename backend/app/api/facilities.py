""" Facility & boundary GeoJSON export """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.database import get_db

router = APIRouter(prefix="/api", tags=["facilities"])

def _table_to_geojson(db, table, geom_col="geometry"):
    rows = db.execute(text(f"SELECT *, ST_AsGeoJSON({geom_col}) AS gj FROM {table}")).fetchall()
    features = []
    for r in rows:
        d = dict(r._mapping)
        gj = d.pop("gj", None)
        if gj:
            import json
            features.append({"type": "Feature", "geometry": json.loads(gj), "properties": {k: v for k, v in d.items() if k != geom_col}})
    return {"type": "FeatureCollection", "features": features}

@router.get("/hospitals/export")
def export_hospitals(db: Session = Depends(get_db)):
    return _table_to_geojson(db, "hospital")

@router.get("/fire-stations/export")
def export_fire_stations(db: Session = Depends(get_db)):
    return _table_to_geojson(db, "fire_station")

@router.get("/shelters/export")
def export_shelters(db: Session = Depends(get_db)):
    return _table_to_geojson(db, "shelter")

@router.get("/boundary/export")
def export_boundary(db: Session = Depends(get_db)):
    return _table_to_geojson(db, "sichuan_boundary")
