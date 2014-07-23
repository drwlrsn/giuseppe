import os
from flask import Flask, request
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
    'images_location_thumbnail': fields.String,
    'images_number': fields.Integer,
    'latitude': fields.Float(attribute='Latitude'),
    'longitude': fields.Float(attribute='Longitude'),
    'bedrooms': fields.Integer(attribute='numb_beds'),
    'bathrooms': fields.Integer,
    'style': fields.String
}

class ListingsRoute(Resource):
    
    def get(self):
        return {'listings': marshal(database.session.query(Listing).all(), listing_fields)}

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

        return {'listings': marshal(query.all(), query_fields)}

api.add_resource(ListingsQueryRoute, '/api/listings/filter')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)