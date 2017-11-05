from flask import render_template
from flask import url_for

from jvanalysis import app

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("home_secured.html")