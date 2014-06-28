import librets, os, os.path
from models.listing import Listing
from database import db_session, init_db
from datetime import datetime
from utils import to_utc

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

def get_all_listings(session, search_request, results=[]):
    print('get_all_listings() called')

    search_results = create_listing_object_list(session.Search(search_request))
    if not search_results:
        return results
    results += search_results

    return get_all_listings(session, \
                              create_listing_search(session, \
                                                    muid_range='{0}+'\
                                                    .format(int(results[-1]\
                                                    .matrix_unique_ID) + 1)), \
                                                    results=results)

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

    try:
        static_dir = os.environ['GIUSEPPE_STATIC_DIR']
    except KeyError:
        static_dir = 'static/images/listings'

    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    for image_format in image_formats:
        dest_dir = static_dir + '/{mls_number}/{format}'\
            .format(mls_number=listing.mls_number, format=image_format.lower())

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

            object_request = librets.GetObjectRequest("Property", image_format)
            object_request.AddAllObjects(listing.matrix_unique_ID)
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

        else:
            num_objects = len([name for name in os.listdir(dest_dir) if os.path.isfile(name)])

        # Update listing object
        listing.images_number = num_objects
        setattr(listing, \
                'images_location_{format}'.format(format=image_format.lower()),\
                dest_dir)

def get_updated_datetime():
    modified = datetime.fromtimestamp(os.path.getmtime('updated'))

    return to_utc(modified)

def datetime_to_rets_time(datetime_obj):
    return datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')

def update_listing_table(session, listings):
    for listing in listings:
        db_obj = db_session.query(Listing).filter_by(matrix_unique_ID = \
                                            int(listing.matrix_unique_ID))\
                                            .first()
        if db_obj == None:
            db_session.add(listing)
        else:
            db_obj.update(listing)
            db_session.add(db_obj)

        db_session.commit()

def get_updated_listings(session):
    """Returns an array of `Listings` that have been updated since 
    `last_update`
    """
    last_updated = datetime_to_rets_time(get_updated_datetime())
    listing_search = create_listing_search(session, \
                                           last_search_datetime=last_updated)
    touch('updated')
    results = session.Search(listing_search)
    listing_objs = create_listing_object_list(results)    

    return listing_objs

def create_session():
    session = librets.RetsSession("http://rets.saskmls.ca/rets/login.ashx")
    session.SetUserAgentAuthType(librets.RETS_1_5)
    session.Login('1075', '3L3ctrick!')

    return session

def main():
    """Entry point if called from the command line"""
    touch('updated')

    session = librets.RetsSession("http://rets.saskmls.ca/rets/login.ashx")
    session.SetUserAgentAuthType(librets.RETS_1_5)
    session.Login('1075', '3L3ctrick!')

    listings_list = []

    while not listings:
        listing_search = create_listing_search(session, limit=-1)
        results = session.Search(listing_search)
        listings = create_listing_object_list(results)

    for listing in listings:
        print(listing)
        #get_listing_images(session, listing)
        db_session.add(listing)
        db_session.commit()



# if __name__ == '__main__':
    # listings = main()



