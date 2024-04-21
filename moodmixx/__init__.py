import flask
from flask_cors import CORS, cross_origin


# app is a single object used by all the code modules in this package
app = flask.Flask(__name__, static_folder='moodmixx/build', static_url_path='')  # pylint: disable=invalid-name
# CORS(app, supports_credentials=True)
CORS(app)

# Read settings from config module (insta485/config.py)
app.config.from_object('moodmixx.config')

import moodmixx.views