import os
from flask import Flask
from database import db_session

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def hello_world():
    return 'Hello, World.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)