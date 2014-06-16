import os
from flask import Flask

app = Flask(__name__)

if os.environ['FLASK_MODE'] == 'STAGING':
	from werkzeug.debug import DebuggedApplication
	app = DebuggedApplication(app, evalex=True)



@app.route('/')
def hello_world():
    return 'Hello, World.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)