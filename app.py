import os
from flask import Flask
from database import db_session
from models.listing import Listing
from models.transit_stop import TransitStop
from flask.ext.restful import Resource, Api, fields, marshal
from flask.ext.restful.utils import cors

app = Flask(__name__)
api = Api(app)
api.decorators=[cors.crossdomain(origin='*')]

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


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
        return {'listings': marshal(db_session.query(Listing).all(), listing_fields)}

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
        return {'transit_stops': marshal(db_session.query(TransitStop).all(), transit_stop_fields)}

api.add_resource(TransitStopsRoute, '/api/transit_stops')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)