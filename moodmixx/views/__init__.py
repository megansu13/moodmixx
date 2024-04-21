from moodmixx import app
from moodmixx.views.spots import spots
from flask_cors import CORS, cross_origin
from flask import send_from_directory

app.register_blueprint(spots)

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# @cross_origin()
# def serve(path):
#     if path != "" and os.path.exists(app.static_folder + '/' + path):
#         return send_from_directory(app.static_folder, path)
#     else:
#         return send_from_directory(app.static_folder, 'index.html')