""" Landslide ORM model """
from sqlalchemy import Column, Integer, Float, String, Text
from geoalchemy2 import Geometry
from ..core.database import Base

class Landslide(Base):
    __tablename__ = "landslide"
    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    province = Column(String)
    city = Column(String)
    county = Column(String)
    town = Column(String)
    trigger = Column(String)
    deaths = Column(Integer)
    injuries = Column(Integer)
    missing = Column(Integer)
    level = Column(String)
    level_full = Column(String)
    geometry = Column(Geometry("POINT", srid=4326))

    @property
    def lon(self):
        from geoalchemy2.shape import to_shape
        return to_shape(self.geometry).x if self.geometry is not None else 0

    @property
    def lat(self):
        from geoalchemy2.shape import to_shape
        return to_shape(self.geometry).y if self.geometry is not None else 0
