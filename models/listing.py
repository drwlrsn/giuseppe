""" Provides a Listing class which represents a residential property in the SRAR RETS system """

from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry
from database import Base


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


class Listing(GeoPointMixin, Base):
    """ A spatially aware class """
    __tablename__ = 'listing'
    id = Column(Integer, primary_key=True)
    matrix_unique_ID = Column(Integer, nullable=False)
    mls_number = Column(Integer, nullable=False)
    list_price = Column(String(10))
    city = Column(String(100))
    address = Column(String(100))
    area_name = Column(String(100))
    sub_area_name = Column(String(100))
    bathrooms = Column(String(10))
    type_dwelling = Column(String(100))
    year_built = Column(String(10))
    sq_footage = Column(String(10))
    parking = Column(String(100))
    outdoor = Column(String(1000))
    numb_rooms = Column(String(10))
    numb_beds = Column(String(10))
    internet_comm = Column(String(2000))
    heating = Column(String(100))
    features = Column(String(1000))
    style = Column(String(100))
    images_location_hires = Column(String(100))
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
                        or a == 'location'
                        or a == 'latitude'
                        or a == 'longitude')])

    def __init__(self, params=None):
        if not params == None:
            self.__dict__.update(params)
            # Check if location data is missing a pass in a zero instead of an
            # empty string.
            if params['Longitude'] == '':
                self.Longitude = 0
            if params['Latitude'] == '':
                self.Latitude = 0

            # Check if longitude is positive. If it is flip it to negative so
            # listing doesn't show up in Russia.
            if not params['Longitude'] == '' and float(params['Longitude']) > 0:
                self.Longitude = -1 * float(params['Longitude'])

            super(Listing, self).__init__(self.Latitude, self.Longitude)

    def __repr__(self):
        return '<Listing {0}>'.format(self.matrix_unique_ID)