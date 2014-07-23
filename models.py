from sqlalchemy import Column, Integer, String
from database import Base
from mixins import GeoGeomMixin, GeoPointMixin
import inspect
from functools import wraps

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
    condo_fees = Column(String(100))
    condo_name = Column(String(200))
    broker_name = Column(String(200))
    Matrix_Modified_DT = Column(String(100))
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


def initializer(func):
    """
    Automatically assigns the parameters.
    Thanks to http://stackoverflow.com/a/1389216/1179222
    >>> class process:
    ...     @initializer
    ...     def __init__(self, cmd, reachable=False, user='root'):
    ...         pass
    >>> p = process('halt', True)
    >>> p.cmd, p.reachable, p.user
    ('halt', True, 'root')
    """
    names, varargs, keywords, defaults = inspect.getargspec(func)

    @wraps(func)
    def wrapper(self, *args, **kargs):
        for name, arg in list(zip(names[1:], args)) + list(kargs.items()):
            setattr(self, name, arg)

        for name, default in zip(reversed(names), reversed(defaults)):
            if not hasattr(self, name):
                setattr(self, name, default)

        func(self, *args, **kargs)

    return wrapper

class School(GeoGeomMixin, Base):
    """ A spatially aware class that represents a school """
    __tablename__ = 'school'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    city = Column(String(100))
    street = Column(String(100))
    house_number = Column(String(50))
    post_code = Column(String(10))
    phone = Column(String(20))
    operator = Column(String(200))
    religion = Column(String(100))
    denomination = Column(String(100))

    @initializer
    def __init__(self, geom, religion=None, denomination=None, **kwargs):
        super(School, self).__init__(geom)


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

class PlaceOfWorship(GeoPointMixin, Base):
    """A spatiallay aware class that represents a place of worship"""
    __tablename__ = 'place_of_worship'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    city = Column(String(100))
    address = Column(String(100))
    post_code = Column(String(10))
    religion = Column(String(100))
    denomination = Column(String(100))

    @initializer
    def __init__(self, latitude=None, longitude=None, religion=None, denomination=None, **kwargs):
        super(PlaceOfWorship, self).__init__(latitude=latitude, longitude=longitude)
    
class SuperMarket(GeoPointMixin, Base):
    """A spatitally aware class that represents a super market"""
    __tablename__ = 'super_market'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    city = Column(String(100))
    street = Column(String(100))
    house_number = Column(String(50))
    post_code = Column(String(10))
    phone = Column(String(20))
    operator = Column(String(200))

    @initializer
    def __init__(self, latitude=None, longitude=None, **kwargs):
        super(SuperMarket, self).__init__(latitude=latitude, longitude=longitude)
