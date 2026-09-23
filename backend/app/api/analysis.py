""" Spatial analysis API """
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.database import get_db

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.get("/buffer")
def buffer_analysis(
    lon: float, lat: float, radius: float = Query(5000, description="radius in meters"),
    db: Session = Depends(get_db),
):
    """ Find facilities within radius of a point """
    results = []
    tables = [("hospital", "医院"), ("fire_station", "消防站"), ("shelter", "避难所")]
    for table, label in tables:
        name_col = '名称' if table in ('hospital', 'fire_station', 'shelter') else 'name'
        rows = db.execute(text(f"""
            SELECT "{name_col}" AS name, ST_Distance(geometry::geography, ST_SetSRID(ST_MakePoint(:lon,:lat),4326)::geography) AS dist
            FROM {table}
            WHERE ST_DWithin(geometry::geography, ST_SetSRID(ST_MakePoint(:lon,:lat),4326)::geography, :radius)
            ORDER BY dist
        """), {"lon": lon, "lat": lat, "radius": radius}).fetchall()
        for r in rows:
            results.append({"type": label, "name": r.name or "-", "distance": round(r.dist)})
    results.sort(key=lambda x: x["distance"])
    return results

@router.get("/nearest")
def nearest_facility(
    lon: float, lat: float, type: str = "hospital", limit: int = Query(5, le=20),
    db: Session = Depends(get_db),
):
    """ Find nearest N facilities of a given type """
    table_map = {"hospital": "医院", "fire_station": "消防站", "shelter": "避难所"}
    table = type if type in table_map else "hospital"
    name_col = '名称'
    rows = db.execute(text(f"""
        SELECT "{name_col}" AS name, ST_Distance(geometry::geography, ST_SetSRID(ST_MakePoint(:lon,:lat),4326)::geography) AS dist
        FROM {table}
        ORDER BY geometry::geography <-> ST_SetSRID(ST_MakePoint(:lon,:lat),4326)::geography
        LIMIT :limit
    """), {"lon": lon, "lat": lat, "limit": limit}).fetchall()
    return [{"type": table_map.get(type, type), "name": r.name or "-", "distance": round(r.dist)} for r in rows]

