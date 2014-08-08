import librets, os, os.path
from models import Listing
from database import db_session, init_db
from datetime import datetime
from utils import to_utc
import logging
from sqlalchemy import func, exc
import shutil
import os

logging.basicConfig(level=logging.DEBUG)

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

def create_listing_search(session, muid_range='0+', area='S1,S2,S3,S5,S5', \
                          limit=-1, last_search_datetime=None, select=None):
    """ Using a :class:`librets.RetsSession` perform a :func:`librets.Search`

    :param session: Authenticated session object
    :session type: :class:`librets.RetsSession`
    :param muid_range: A range of SRAR matrix_unique_ID conforming to a DQML2 
                        query. Default is to begin at the lowest with no upper 
                        bound.
    :muid_range type: str
    :param area: A DQML2 formatted string of SRAR `area_name`s. The default is 
                    a string of comma separated area names representing 
                    Saskatoon.
    :area type: str
    :param limit: A number limiting the number of results returned by the 
                    search.
    :limit type: int
    :returns: A `SearchRequest` to be used in :func:`librets.RetsSession.Search`
    :rtype: :class:`librets.SearchRequest`
    """
    if not select:
        select = Listing().select_string

    if last_search_datetime == None:
        search_request = session.CreateSearchRequest(\
                'Property', 'RESI', \
                '(matrix_unique_ID={muid_range}),(area_name={area_name})'\
                .format(muid_range=muid_range, area_name=area))
    else:
        search_request = session.CreateSearchRequest(\
                'Property', 'RESI', \
                '(Matrix_Modified_DT={modified}+),(area_name={area_name})'\
                .format(modified=last_search_datetime, area_name=area))

    search_request.SetSelect(select)
    search_request.SetLimit(limit)
    search_request.SetCountType(librets.SearchRequest.RECORD_COUNT_AND_RESULTS)
    search_request.SetFormatType(librets.SearchRequest.COMPACT_DECODED)

    return search_request


def create_listing_object_list(results):
    """ Takes the results of :func:`librets.RetsSession.Search` and returns a 
    list of :class:`Listing` objects ready to be serialised to the database.

    :param results: The results of a :func:`librets.RetsSession.Search`
    :type results: `librets.SearchResultSet`
    :returns: A list of `Listing` objects
    :rtype: list
    """

    columns = results.GetColumns()
    listings_list = []

    while results.HasNext():
        listing_dict = {}
        for column in columns:
            listing_dict[column] = results.GetString(column)

        listings_list.append(Listing(listing_dict))

    return listings_list

def get_all_listings(session, list=True, muid_range='0+', area='S1,S2,S3,S5,S5', \
                          limit=-1, last_search_datetime=None, select=None, results=[]):
    logging.debug('GET ALL LISTINGS\nget_all_listings(list={list}, muid_range={muid_range}, area={area}, \
          limit={limit}, last_search_datetime={last_search_datetime}, \
          select={select}) called'.format(list=list, muid_range=muid_range, \
                                            area=area, limit=limit, \
                                            last_search_datetime=last_search_datetime, \
                                            select=select))
    search_request = create_listing_search(session, muid_range, area, limit, \
                                           last_search_datetime, select)
    if list:
        search_results = create_listing_muid_list(session.Search(search_request))
    else:
        search_results = create_listing_object_list(session.Search(search_request))
    
    if not search_results:
        return results
    results += search_results

    try:
        muid_range='{0}+'.format(int(results[-1].matrix_unique_ID) + 1)
    except AttributeError:
        muid_range='{0}+'.format(int(results[-1]) + 1)

    return get_all_listings(session, muid_range=muid_range, area=area, limit=limit, last_search_datetime=last_search_datetime, select=select, results=results)

def create_listing_muid_list(results):
    """ Takes the results of :func:`librets.RetsSession.Search` and returns a 
    list of :class:`Listing` objects ready to be serialised to the database.

    :param results: The results of a :func:`librets.RetsSession.Search`
    :type results: `librets.SearchResultSet`
    :returns: A list of `Listing` objects
    :rtype: list
    """

    columns = results.GetColumns()
    listings_list = []

    while results.HasNext():
        listings_list.append(results.GetString('matrix_unique_ID'))

    return listings_list

def get_listing_images(session, listing):
    """ Given a :class:`Listing` this function downloads all images associated
        with it creating a :class:`librets.GetObjectRequest` and executing a
        :func:`librets.RetsSession.GetObject` and modifies the :class:`Listing`.
    :param listing: a property listing object
    :listing type: :class:`Listing`
    :param session: Authenticated session object
    :session type: :class:`librets.RetsSession`
    :returns: A a of strings that are the directories where the various images 
        of that listing have been saved. Exam
    :rtype: tuple
    """

    image_formats = ('HiRes', 'Photo', 'Thumbnail')
    logging.info('GET LISTING IMAGE')
    try:
        static_dir = os.environ['GIUSEPPE_STATIC_DIR']
    except KeyError:
        static_dir = 'static/images/listings'

    logging.info('Saving images to {0}'.format(static_dir))
    if not os.path.exists(static_dir):
        logging.info('{0} doesn\'t exist. Creating it.'.format(static_dir))
        os.makedirs(static_dir)

    for image_format in image_formats:
        dest_dir = static_dir + '/{mls_number}/{format}'\
            .format(mls_number=listing.mls_number, format=image_format.lower())

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        object_request = librets.GetObjectRequest("Property", image_format)
        object_request.AddAllObjects(str(listing.matrix_unique_ID))
        response = session.GetObject(object_request)
    
        object_descriptor = response.NextObject()
        num_objects = 0
        while (object_descriptor != None):
            # object_key = object_descriptor.GetObjectKey()
            object_id = object_descriptor.GetObjectId()
            # content_type = object_descriptor.GetContentType()

            with open('{dest_dir}/image-{id}.jpg'.format(dest_dir=dest_dir, \
                      id=object_id), 'wb') as image_file:
                image_file.write(object_descriptor.GetData())
                image_file.close()

            num_objects += 1
            object_descriptor = response.NextObject()

        # Update listing object
        listing.images_number = num_objects
        setattr(listing, \
                'images_location_{format}'.format(format=image_format.lower()),\
                dest_dir)
        logging.info('Updated {0} {1} images for listing {2}'.format(num_objects, image_format, listing.matrix_unique_ID))

def get_updated_datetime():
    modified = datetime.fromtimestamp(os.path.getmtime('updated'))

    return to_utc(modified)

def datetime_to_rets_time(datetime_obj):
    return datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')

def update_listing_table(session):
    logging.info('UPDATE LISTINGS')
    listings = get_updated_listings(session)
    for listing in listings:
        result = db_session.query(Listing).filter_by(matrix_unique_ID = \
                                            int(listing.matrix_unique_ID))\
                                            .first()
        if result == None:
            logging.debug('Listing {0} not found. Adding to session.'.format(listing))
            db_session.add(listing)
        else:
            logging.debug('Listing {0} found. Updating object and merging in session.'.format(listing))
            listing.id = result.id
            db_session.merge(listing)

        get_listing_images(session, listing)

        db_session.commit()

        logging.debug('Updated {0}'.format(listing.matrix_unique_ID))

    logging.info('Updated {0} listings.'.format(len(listings)))

def get_updated_listings(session):
    """Returns an array of `Listings` that have been updated since 
    `last_update`
    """
    touch('updated')
    last_updated = datetime_to_rets_time(get_updated_datetime())
    listing_search = create_listing_search(session, \
                                           last_search_datetime=last_updated)
    results = session.Search(listing_search)
    listing_objs = create_listing_object_list(results)    

    logging.info('Found {0} listings since {1}'.format(len(listing_objs), last_updated))

    return listing_objs

def create_session():
    session = librets.RetsSession("http://rets.saskmls.ca/rets/login.ashx")
    session.SetUserAgentAuthType(librets.RETS_1_5)
    session.SetModeFlags = session.MODE_NO_EXPECT
    try:
        session.Login('1075', '3L3ctrick!')
    except:
        logging.critical("Unable to login to SRAR RETS.")

    return session

def clean_listing_images(session, listings):
    logging.info('CLEAN LISTING IMAGES')
    try:
        listings_image_dir = os.environ['GIUSEPPE_STATIC_DIR']
    except KeyError:
        listings_image_dir = 'static/images/listings'

    for listing in listings:
        logging.debug('Cleaning listing {0}'.format(listing.matrix_unique_ID))
        try:
            shutil.rmtree(os.path.join(listings_image_dir, str(listing.mls_number)))
            logging.debug('Removed listing {0}'.format(listing.matrix_unique_ID))
        except FileNotFoundError as error:
            logging.error('Could not remove image directors for listing {0}.'.format(listing.matrix_unique_ID))
            logging.exception(error)
    logging.info('Successfully removed images for {0} listings.'.format(len(listings)))

def clean_listings():
    """Removes listings that no longer appear in SRAR RETS DB"""
    logging.info('CLEAN LISTINGS')
    session = create_session()
    listings = get_all_listings(session, select='matrix_unique_ID')
    logging.debug("Listings to be cleaned: {0}".format(listings))
    stale_listings = db_session.query(Listing).filter(~Listing.matrix_unique_ID.in_(listings)).all()
    num_listings = len(stale_listings)

    clean_listing_images(session, stale_listings)

    try:
        db_session.query(Listing.matrix_unique_ID).filter(~Listing.matrix_unique_ID.in_(listings)).delete(synchronize_session='fetch')
        db_session.commit()
        logging.info('Removed {0} listings.'.format(num_listings))
        logging.debug('Listings removed: {0}'.format(', '.join([str(listing.matrix_unique_ID) for listing in stale_listings])))
    except Exception as error:
        db_session.rollback()
        logging.critical('Failed clean listings!')
        logging.exception(error)

def fix_listing_images(session):
    logging.info('FIX LISTING IMAGES')
    results = db_session.query(Listing).filter_by(images_location_hires = None).all()
    logging.info('Found {0} listings missing images.'.format(len(results)))
    for result in results:
        get_listing_images(session, result)

        try:
            db_session.commit()
        except exc.InvalidRequestError as error:
            logging.error('Could not commit changes to database!')
            logging.exception(error)

    logging.info('Fixed listing images.')


def main():
    """Entry point if called from the command line"""
    logging.info('RECREATING LISTING TABLE')
    rows_deleted = db_session.query(Listing).delete()
    logging.info('Deleted {0} rows.'.format(rows_deleted))

    session = create_session()
    touch('updated')
    listings = get_all_listings(session, list=False)
    for listing in listings:
        get_listing_images(session, listing)
    db_session.add_all(listings)
    db_session.commit()

    logging.info('Added {0} listings.'.format(len(listings)))

if __name__ == '__main__':
    main()



