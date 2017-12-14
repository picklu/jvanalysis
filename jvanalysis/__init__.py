from flask import Flask

from flask_jsglue import JSGlue
from flask_login import LoginManager
from flask_session import Session

from jvanalysis.jvhelper import nice_date
from jvanalysis.jvhelper import nice_number
from jvanalysis.jvhelper import ObjectIDConverter
from jvanalysis.jvhelper import nicefy

from pymongo import MongoClient

app = Flask(__name__)
app.url_map.converters['objectid'] = ObjectIDConverter
app.config.from_object('config.DevelopmentConfig')
app.config['SESSION_MONGODB'] = MongoClient()

app.jinja_env.filters['nicefy'] = nicefy
app.jinja_env.filters['nicedate'] = nice_date
app.jinja_env.filters['nicenum'] = nice_number

JSGlue(app)
login_manager = LoginManager(app)
Session(app)

import jvanalysis.views