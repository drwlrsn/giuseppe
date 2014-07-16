import overpass, overpass.execute, overpass.nodes
from models import PlaceOfWorship
import database
import time, urllib.request, json, logging
logging.basicConfig(level=logging.DEBUG)

class YellowAPI:
    def __init__(self, what, where, uid, apikey, pglen=40, page=1, format='JSON'):
        self.what = what
        self.where = where
        self.pglen = pglen
        self.uid = uid
        self.apikey = apikey
        self.page = page
        self.format = format

    def find_business(self, page=None):
        if not page:
            page = self.page
        url = 'http://api.sandbox.yellowapi.com/FindBusiness/?what={what}&where={where}&pgLen={pglen}&pg={page}&dist=1&fmt={format}&lang=en&UID={uid}&apikey={apikey}'
        url = url.format(what=self.what, where=self.where, pglen=self.pglen, page=page, format=self.format, uid=self.uid, apikey=self.apikey)

        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def get_all_listings(self):
        response = self.find_business()
        listings = response['listings']
        logging.debug('Searching YellowAPI for {what}.'.format(what=self.what))
        logging.debug('Found {0} results across {1} pages.'.format(response['summary']['totalListings'], response['summary']['pageCount']))

        for page_num in range(2, int(response['summary']['pageCount']) + 1):
            time.sleep(2.5)
            response = self.find_business(page=page_num)
            logging.debug('Current request page is {0}.'.format(response['summary']['currentPage']))
            logging.debug('First listing on page is {0}.'.format(response['summary']['firstListing']))
            logging.debug('Last listing on page is {0}'.format(response['summary']['lastListing']))

            listings.extend(response['listings'])

        return listings

def get_churches():
    yellowapi = YellowAPI(
                          what='church',
                          where='Saskatoon',
                          uid='127.0.0.1',
                          apikey='w4wssbppkvctta74jma89jf9')

    return yellowapi.get_all_listings()

def get_synagogues():
    yellowapi = YellowAPI(
                          what='synagogue',
                          where='Saskatoon',
                          uid='127.0.0.1',
                          apikey='w4wssbppkvctta74jma89jf9')

    return yellowapi.get_all_listings()


def serialise(pow, religion=None):
    if not pow['geoCode']:
        logging.error('{0} in {1} doesn\'t have spatial data'.format(pow['name'], pow['address']['city']))
        return

    new_pow = PlaceOfWorship(
                             name=pow['name'],
                             latitude=pow['geoCode']['latitude'],
                             longitude=pow['geoCode']['longitude'],
                             city=pow['address']['city'],
                             address=pow['address']['street'],
                             post_code=pow['address']['pcode']
                             )
    if religion:
        new_pow.religion = religion

    database.session.add(new_pow)
    database.session.commit()
