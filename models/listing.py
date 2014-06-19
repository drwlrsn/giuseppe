""" Provides a Listing class which represents a residential property in the SRAR RETS system """

from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry
from database import Base


class GeoPointMixin:
    Latitude = Column(Float)
    Longitude = Column(Float)
    location = Column(Geometry(geometry_type='POINT', srid=4326))

    def __init__(self, latitude, longitude):
        self.location = 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)


class Listing(GeoPointMixin, Base):
    """ A spatially aware class """
    __tablename__ = 'listing'
    id = Column(Integer, primary_key=True)
    matrix_unique_ID = Column(Integer)
    mls_number = Column(Integer)
    list_price = Column(Float)
    city = Column(String(25))
    address = Column(String(50))
    area_name = Column(String(25))
    sub_area_name = Column(String(25))
    bathrooms = Column(Integer)
    type_dwelling = Column(String(25))
    year_built = Column(Integer)
    sq_footage = Column(Float)
    parking = Column(String(25))
    outdoor = Column(String(100))
    numb_rooms = Column(Integer)
    numb_beds = Column(Integer)
    internet_comm = Column(String(2000))
    heating = Column(String(100))
    features = Column(String(100))
    style = Column(String(25))
    images_location_highres = Column(String(100))
    images_location_photo = Column(String(100))
    images_location_thumbnail = Column(String(100))
    images_number = Column(Integer)

    @property
    def select_string(self):
        """
        Return a string of class attributes which SRAR residential property
        selects.

        :returns: A comma separated list of attributes.
        :rtype: str
        """
        return ','.join([a for a in dir(self) if not(a.startswith('__') \
                        and a.endswith('__') \
                        or a == 'select_string' \
                        or a.startswith('images_') \
                        or a.startswith('_') \
                        or a == 'metadata' \
                        or a == 'query' \
                        or a == 'id'
                        or a == 'location')])

    def __init__(self, params=None):
        if not params == None:
            self.__dict__.update(params)
            super(Listing, self).__init__(self.Latitude, self.Longitude)

    def __repr__(self):
        return '<Listing {0}>'.format(self.matrix_unique_ID)