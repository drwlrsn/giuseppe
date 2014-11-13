import overpass, overpass.execute, overpass.nodes
from models import PlaceOfWorship
import database
import time, urllib.request, json, logging
logging.basicConfig(level=logging.INFO)

class YellowAPI:
    def __init__(self, what, where, uid, apikey, pglen=40, page=1, format='JSON', dist=1):
        self.what = what
        self.where = where
        self.pglen = pglen
        self.uid = uid
        self.apikey = apikey
        self.page = page
        self.format = format
        self.dist = dist

    def find_business(self, page=None):
        if not page:
            page = self.page
        url = 'http://api.sandbox.yellowapi.com/FindBusiness/?what={what}&where={where}&pgLen={pglen}&pg={page}&dist={dist}&fmt={format}&lang=en&UID={uid}&apikey={apikey}'
        url = url.format(what=self.what, where=self.where, pglen=self.pglen, page=page, dist=self.dist, format=self.format, uid=self.uid, apikey=self.apikey)

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
    yellowapi_saskatoon = YellowAPI(
                          what='church',
                          where='Saskatoon',
                          uid='127.0.0.1',
                          apikey='w4wssbppkvctta74jma89jf9')

    yellowapi_warman = YellowAPI(
                          what='church',
                          where='Warman',
                          uid='127.0.0.1',
                          apikey='w4wssbppkvctta74jma89jf9')

    yellowapi_martensville = YellowAPI(
                          what='church',
                          where='Martensville',
                          uid='127.0.0.1',
                          apikey='w4wssbppkvctta74jma89jf9')

    results = yellowapi_saskatoon.get_all_listings()
    time.sleep(1.1)
    results += yellowapi_warman.get_all_listings()
    time.sleep(1.1)
    results += yellowapi_martensville.get_all_listings()

    return results

def get_synagogues():
    yellowapi = YellowAPI(
                          what='synagogue',
                          where='Saskatoon',
                          uid='127.0.0.1',
                          apikey='w4wssbppkvctta74jma89jf9')

    return results


def serialise(pow, religion=None, debug=True):
    if not pow['geoCode']:
        logging.debug('Skipping. {0} in {1} doesn\'t have spatial data'.format(pow['name'], pow['address']['city']))
        return
    
    if not pow['address']['city'].rstrip() == 'Saskatoon' and not pow['address']['city'].rstrip()  == 'Warman' \
      and not pow['address']['city'].rstrip() == 'Martensville':
        logging.debug('Skipping. {name} in {city}'.format(name=pow['name'], city=pow['address']['city']))  
        return

    exclusions = (
                 'office',
                 'rectory',
                 'manestreet',
                 'enterprise',
                 'library',
                 'mission',
                 'mennonite central committee',
                 'demczuk b rev',
                 'waschuk john f rev',
                 'student residence',
                 'corporation',
                 'kitchen'
                 )
    for exclusion in exclusions:
      if exclusion in pow['name'].lower():
        return


    # Check to see if in database
    query = database.session.query(PlaceOfWorship)
    if query.filter_by(name=pow['name']).first():
        logging.debug('Skipping. {name} already in database.'.format(name=pow['name']))
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

    if not debug:
      database.session.add(new_pow)
      database.session.commit()
      logging.info('Saved {name} in {city} to database.'.format(name=new_pow.name, city=new_pow.city))
    else:
      logging.debug('Saving {name} to datase'.format(name=new_pow.name))
