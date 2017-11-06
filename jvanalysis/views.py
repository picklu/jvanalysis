from flask import render_template
from flask import url_for

from jvanalysis import app

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home_secured.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/account")
def account():
    return render_template("account.html")

@app.route("/analysis")
def analysis():
    return render_template("analysis.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signout")
def signout():
    return index()