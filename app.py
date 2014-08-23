import os
from flask import Flask, request, send_from_directory
import database
from models import *
from flask.ext.restful import Resource, Api, fields, marshal
from flask.ext.restful.utils import cors

app = Flask(__name__)
api = Api(app)
api.decorators=[cors.crossdomain(origin='*')]

@app.teardown_appcontext
def shutdown_session(exception=None):
    database.session.remove()


listing_fields = {
    'id': fields.Integer,
    'mls_number': fields.Integer,
    'list_price': fields.Float,
    'address': fields.String,
    'images_location': fields.String(attribute='images_location_photo'),
    'images_large': fields.String(attribute='images_location_hires'),
    'images_number': fields.Integer,
    'latitude': fields.Float(attribute='Latitude'),
    'longitude': fields.Float(attribute='Longitude'),
    'bedrooms': fields.Integer(attribute='numb_beds'),
    'bathrooms': fields.Integer,
    'style': fields.String,
    'broker_name': fields.String,
    'neighbourhood': fields.String(attribute='sub_area_name'),
    'type_dwelling': fields.String,
    'condo_fees': fields.Float,
    'description': fields.String(attribute='internet_comm'),
    'sq_footage': fields.String,
    'year_built': fields.String,
    'condo_name': fields.String
}

class ListingsRoute(Resource):
    
    def get(self):
        import csv
        query = database.session.query(Listing).distinct(Listing.id)

        if request.args:
            degrees_metre = 1 / 78710
            priceLow = request.args.get('priceLow', None, type=float)
            priceHigh = request.args.get('priceHigh', None, type=float)
            supermarket_radius = request.args.get('supermarket', None, type=float)
            pow_radius = request.args.get('place_of_worship', None, type=float)
            transit_radius = request.args.get('transit_stop', None, type=float)
            school_radius = request.args.get('school', None, type=float)
            neighbourhood = request.args.get('neighbourhood', None)
            bedrooms = request.args.get('bedrooms', None, type=int)
            bathrooms = request.args.get('bathrooms', None, type=int)
            school_filter = request.args.get('schoolFilter', None, type=str)
            type = request.args.get('type', None, type=str)

            if priceLow:
                query = query.filter(Listing.list_price >= priceLow)

            if priceHigh:
                query = query.filter(Listing.list_price <= priceHigh)

            if neighbourhood:
                query = query.filter(Listing.sub_area_name.startswith(neighbourhood))

            if bedrooms:
                query = query.filter(Listing.numb_beds >= bedrooms)

            if bathrooms:
                query = query.filter(Listing.bathrooms >= bathrooms)

            if type:
                if type == 'condominium':
                    query = query.filter(Listing.type_dwelling == 'CONDOMINIUM')
                if type == 'vacant lot':
                    query = query.filter(Listing.type_dwelling == 'VACANT LOT')
                if type == 'residential':
                    query = query.filter(Listing.type_dwelling != 'VACANT LOT').filter(Listing.type_dwelling != 'CONDOMINIUM')

            if supermarket_radius:
                query = query.join(SuperMarket, SuperMarket.location.ST_DWithin(Listing.location, supermarket_radius * degrees_metre))

            if pow_radius:
                query = query.join(PlaceOfWorship, PlaceOfWorship.location.ST_DWithin(Listing.location, pow_radius * degrees_metre))

            if transit_radius:
                query = query.join(TransitStop, TransitStop.location.ST_DWithin(Listing.location, transit_radius * degrees_metre))

            if school_radius:
                if school_filter:
                    school_boards = school_filter.split(',')
                    if 'catholic' in school_boards:
                        query = query.join(School, School.geom.ST_DWithin(Listing.location, school_radius * degrees_metre)).filter(School.operator == 'Greater Saskatoon Catholic Schools')
                    if 'public' in school_boards:
                        query = query.join(School, School.geom.ST_DWithin(Listing.location, school_radius * degrees_metre)).filter(School.operator == 'Saskatoon Public Schools')
                    if 'other' in school_boards:
                        query = query.join(School, School.geom.ST_DWithin(Listing.location, school_radius * degrees_metre)).filter(School.operator != 'Saskatoon Public Schools').filter(School.operator != 'Greater Saskatoon Catholic Schools')
                else:
                    query = query.join(School, School.geom.ST_DWithin(Listing.location, school_radius * degrees_metre))
        
        results = query.all()
        return {'listings': marshal(results, listing_fields)}

api.add_resource(ListingsRoute, '/api/listings')

transit_stop_fields = {
    'id': fields.Integer,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'code': fields.String,
    'name': fields.String
}

class TransitStopsRoute(Resource):
    def get(self):
        return {'transit_stops': marshal(database.session.query(TransitStop).all(), transit_stop_fields)}

api.add_resource(TransitStopsRoute, '/api/transit_stops')

school_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'city': fields.String,
    'street': fields.String,
    'house_number': fields.String,
    'operator': fields.String,
    'religion': fields.String,
    'denomination': fields.String,
    'latitude': fields.Float,
    'longitude': fields.Float
}

class SchoolsRoute(Resource):
    def get(self):
        return {'schools': marshal(database.session.query(School).all(), school_fields)}

api.add_resource(SchoolsRoute, '/api/schools')

placesofworship_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'city': fields.String,
    'street': fields.String,
    'religion': fields.String,
    'latitude': fields.Float,
    'longitude': fields.Float
}

class PlacesOfWorshipRoute(Resource):
    def get(self):
        return {'pows': marshal(database.session.query(PlaceOfWorship).all(), placesofworship_fields)}

api.add_resource(PlacesOfWorshipRoute, '/api/pows')

supermarkets_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'latitude': fields.Float,
    'longitude': fields.Float
}

class SuperMarketsRoute(Resource):
    def get(self):
        return {'supermarkets': marshal(database.session.query(SuperMarket).all(), supermarkets_fields)}

api.add_resource(SuperMarketsRoute, '/api/supermarkets')

query_fields = {
    'id': fields.Integer
}

class ListingsQueryRoute(Resource):
    def get(self):
        """Possible parameters are `supermarket`, `place_of_worship`, `transit_stop`, `school`"""

        supermarket_radius = request.args.get('supermarket', None, type=float)
        pow_radius = request.args.get('place_of_worship', None, type=float)
        transit_radius = request.args.get('transit_stop', None, type=float)
        school_radius = request.args.get('school', None, type=float)

        degrees_metre = 1 / 78710

        query = database.session.query(Listing).distinct(Listing.id)

        if supermarket_radius:
            query = query.join(SuperMarket, SuperMarket.location.ST_DWithin(Listing.location, supermarket_radius * degrees_metre))

        if pow_radius:
            query = query.join(PlaceOfWorship, PlaceOfWorship.location.ST_DWithin(Listing.location, pow_radius * degrees_metre))

        if transit_radius:
            query = query.join(TransitStop, TransitStop.location.ST_DWithin(Listing.location, transit_radius * degrees_metre))

        if school_radius:
            query = query.join(School, School.geom.ST_DWithin(Listing.location, school_radius * degrees_metre))

        return {'listings': marshal(query.all(), listing_fields)}

api.add_resource(ListingsQueryRoute, '/api/listings/filter')

import os
@app.route('/static/<path:path>')
def send_foo(path):
    return app.send_static_file(os.path.join('static/', path))



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)