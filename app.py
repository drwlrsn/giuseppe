import os
from flask import Flask
from database import db_session
from models.listing import Listing
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
}

class ListingsRoute(Resource):
    
    def get(self):
        return {'listings': marshal(db_session.query(Listing).all(), listing_fields)}

api.add_resource(ListingsRoute, '/api/listings')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)