from flask import Flask
from flask_jsglue import JSGlue

app = Flask(__name__)
app.config.from_object('jvanalysis.config.DevelopmentConfig')
JSGlue(app)

import jvanalysis.views