from flask import Flask
from flask_jsglue import JSGlue
from flask_login import LoginManager
from jvanalysis.jvhelper import ObjectIDConverter
from jvanalysis.jvhelper import nicefy

app = Flask(__name__)
app.url_map.converters['objectid'] = ObjectIDConverter
app.config.from_object('config.DevelopmentConfig')
app.jinja_env.filters['nicefy'] = nicefy
JSGlue(app)
login_manager = LoginManager(app)

import jvanalysis.views