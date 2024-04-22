from moodmixx import app
from moodmixx.views.spots import spots

app.register_blueprint(spots)