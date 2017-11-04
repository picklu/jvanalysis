from flask import Flask

app = Flask(__name__)
app.config.from_object('jvanalysis.config.DevelopmentConfig')

import jvanalysis.views