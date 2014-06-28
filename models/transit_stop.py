""" Transit stops """

from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry
from database import Base
from models.listing import GeoPointMixin

class TransitStop(GeoPointMixin, Base):
    """ A spatially aware class that represents a transit stop """
    __tablename__ = 'transit_stop'
    id = Column(Integer, primary_key=True)
    code = Column(String(200))
    name = Column(String(200))

    def __init__(self, code=None, name=None, latitude=None, longitude=None):
        self.code = code
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

        super(TransitStop, self).__init__(latitude=latitude, longitude=longitude)
