import flask
from flask_cors import CORS, cross_origin
from flask import send_from_directory

from .views.spots import spots
from flask_cors import CORS, cross_origin


def create_app():
    # app is a single object used by all the code modules in this package
    app = flask.Flask(__name__, static_folder='moodmixx/build', static_url_path='')  # pylint: disable=invalid-name
    # CORS(app, supports_credentials=True)
    CORS(app)

# Read settings from config module (insta485/config.py)
    app.config.from_object('moodmixx.config')
    app.register_blueprint(spots)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    @cross_origin()
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')