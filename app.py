import os
from flask import Flask
from database import db_session
from models.listing import Listing
from flask.ext.restful import Resource, Api, fields, marshal_with

app = Flask(__name__)
api = Api(app)

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
    'Latitude': fields.Float,
    'Longitude': fields.Float,
}

class ListingsRoute(Resource):
    @marshal_with(listing_fields)
    def get(self):
        return db_session.query(Listing).get(1)

api.add_resource(ListingsRoute, '/listing')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)