from flask import Flask
from flask_jsglue import JSGlue
from jvanalysis.jvhelper import ObjectIDConverter

app = Flask(__name__)
app.url_map.converters['objectid'] = ObjectIDConverter
app.config.from_object('config.DevelopmentConfig')
JSGlue(app)

import jvanalysis.views