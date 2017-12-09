from flask import Flask
from flask_jsglue import JSGlue
from flask_login import LoginManager
from jvanalysis.jvhelper import ObjectIDConverter

app = Flask(__name__)
app.url_map.converters['objectid'] = ObjectIDConverter
app.config.from_object('config.DevelopmentConfig')
JSGlue(app)
login_manager = LoginManager(app)

import jvanalysis.views