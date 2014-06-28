import pytz
from models.transit_stop import TransitStop
import sys, csv
from database import db_session

def to_utc(dt):
    u"""Coverts a datetime which is in the local time

    Args:
        dt (dt): A timezone naive object created at the local time

    Returns:
        datetime  A datetime object in the UTC timezone.

    """
    cst = pytz.timezone(u'America/Regina')
    localized_datetime = cst.localize(dt)

    return localized_datetime.astimezone(pytz.UTC)
    

def load_transit_stops(transit_stops_file):
    transit_stops = []
    with open(transit_stops_file, 'r') as f:
        reader = csv.reader(f)
        row_num = 0
        for row in reader:
            new_stop = TransitStop(
                           code=row[1], \
                           name=row[3], \
                           latitude=row[5], \
                           longitude=row[6])
            if not row_num == 0:
                transit_stops.append(new_stop)
            row_num += 1

    print(len(transit_stops))
    db_session.add_all(transit_stops)
    db_session.commit()
