from flask import render_template, request
from flask import url_for

from jvanalysis import app
from jvanalysis.jvplot import INLINE, resources


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/home")
def home():
    return render_template("home_secured.html")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/account")
def account():
    return render_template("account.html", title="Account")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html", title="Analysis")


@app.route("/dashboard")
def dashboard():
    bkdiv, bkscript = resources()
    return render_template(
        "dashboard.html",
        bkjs=INLINE.render_js(),
        bkcss= INLINE.render_css(),
        bkdiv=bkdiv,
        bkscript=bkscript,
        title="Dashboard")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", title="Sign up")
    return index()


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html", title="Sign in")
    return index()


@app.route("/signout", methods=["POST"])
def signout():
    return index()


@app.route("/guest")
def guest():
    return home()
