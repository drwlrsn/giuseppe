import librets, os, os.path
from models.listing import Listing
from database import db_session, init_db

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

def create_listing_search(session, muid_range='0+', area='S1,S2,S3,S5,S5', \
                          limit=100):
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

    search_request = session.CreateSearchRequest(\
            'Property', 'RESI', \
            '(matrix_unique_ID={muid_range}),(area_name={area_name})'\
            .format(muid_range=muid_range,area_name=area))
    search_request.SetLimit(limit)
    search_request.SetSelect(Listing().select_string)
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

def main():
    """Entry point if called from the command line"""
    touch('updated')

    session = librets.RetsSession("http://rets.saskmls.ca/rets/login.ashx")
    session.SetUserAgentAuthType(librets.RETS_1_5)
    session.Login('1075', '3L3ctrick!')

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



