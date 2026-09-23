""" Landslide Pydantic schemas """
from pydantic import BaseModel
from typing import Optional

class LandslideCreate(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    province: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    town: Optional[str] = None
    trigger: Optional[str] = None
    deaths: int = 0
    injuries: int = 0
    missing: int = 0
    level: Optional[str] = None
    level_full: Optional[str] = None
    lon: float
    lat: float

class LandslideUpdate(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    province: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    town: Optional[str] = None
    trigger: Optional[str] = None
    deaths: Optional[int] = None
    injuries: Optional[int] = None
    missing: Optional[int] = None
    level: Optional[str] = None
    level_full: Optional[str] = None
    lon: Optional[float] = None
    lat: Optional[float] = None

class LandslideOut(BaseModel):
    id: int
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    province: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    town: Optional[str] = None
    trigger: Optional[str] = None
    deaths: int = 0
    injuries: int = 0
    missing: int = 0
    level: Optional[str] = None
    level_full: Optional[str] = None
    lon: float
    lat: float
    model_config = {"from_attributes": True}
