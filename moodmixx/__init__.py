import flask
from flask_cors import CORS


# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name
CORS(app, supports_credentials=True)

# Read settings from config module (insta485/config.py)
app.config.from_object('moodmixx.config')

import moodmixx.views