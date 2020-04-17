from flask import Flask
from flask_jsglue import JSGlue
from flask_login import LoginManager
from flask_session import Session
from flask_pymongo import MongoClient
from jvanalysis.jvhelper import (nice_date, nice_number, ObjectIDConverter,
                                 nicefy)

app = Flask(__name__)

app.url_map.converters['objectid'] = ObjectIDConverter
app.config.from_object('config.ProductionConfig')
app.config["SESSION_MONGODB"] = MongoClient(app.config["MONGO_SESSION_URI"])
app.jinja_env.filters['nicefy'] = nicefy
app.jinja_env.filters['nicedate'] = nice_date
app.jinja_env.filters['nicenum'] = nice_number
JSGlue(app)
login_manager = LoginManager(app)
Session(app)

import jvanalysis.views
