from sync import *
session = create_session()
clean_listings()
update_listing_table(session)