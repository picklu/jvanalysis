from flask import render_template
from flask import request
from flask import json
from flask import url_for

from jvanalysis import app
from jvanalysis.jvplot import INLINE, resources, get_params


JVDATA = {}

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

@app.route("/plot/<path:path>")
def plot(path=""):
    bkdiv, bkscript = resources("jV Plot of " + path)
    return render_template(
        "plot.html",
        bkjs=INLINE.render_js(),
        bkcss=INLINE.render_css(),
        bkdiv=bkdiv,
        bkscript=bkscript,
        title="plot|" + path if path else "plot")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.form
    jv_data = json.loads(data.get("jv"))
    params = get_params(jv_data)
    return json.dumps(params)

@app.route("/analysis")
def analysis():
    return render_template("analysis.html", title="Analysis")


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
