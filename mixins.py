from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry
from geoalchemy2 import func
import database

class GeoGeomMixin:
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))

    def __init__(self, geom):
        self._set_geom(geom)

    def _set_geom(self, geom):
        self.geom = 'SRID=4326;POLYGON(({0}))'.format(','.join(geom))

    def _get_centroid(self):
        """Returns `WKBElement`"""
        return database.session.scalar(self.geom.ST_Centroid())

    @property
    def latitude(self):
        centroid = self._get_centroid()
        return database.session.scalar(func.ST_X(centroid))

    @property
    def longitude(self):
        centroid = self._get_centroid()
        return database.session.scalar(func.ST_Y(centroid))


class GeoPointMixin:
    Latitude = Column(Float)
    Longitude = Column(Float)
    location = Column(Geometry(geometry_type='POINT', srid=4326))

    def __init__(self, latitude=0, longitude=0):
        self.location = 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)

    @property
    def latitude(self):
        """Provide a `latitude` property"""
        return self.Latitude

    @latitude.setter
    def latitude(self, lat):
        self.Latitude = lat

    @property
    def longitude(self):
        """Provide a `longitude` property"""
        return self.Longitude

    @longitude.setter
    def longitude(self, long):
        self.Longitude = long