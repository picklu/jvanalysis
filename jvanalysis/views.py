from flask import render_template
from flask import request
from flask import json
from flask import url_for

from jvanalysis import app
from jvanalysis.jvplot import DATA_FOLDER
from jvanalysis.jvplot import resources
from jvanalysis.jvplot import get_params
from jvanalysis.jvplot import get_resources

filename = DATA_FOLDER + "/analyze.json"

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
    if path == "analyzed" in path:
        with open(filename, "r") as jsonfile:
            data = json.load(jsonfile)
        bkdiv, bkscript = get_resources("jV plot of analyzed data", data)
    else:
        bkdiv, bkscript = resources("jV Plot of " + path)
    return render_template(
        "plot.html",
        bkdiv=bkdiv,
        bkscript=bkscript,
        title="plot|" + path if path else "plot")

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    data = request.form.get("jv")
    jv_data = json.loads(data)
    params = get_params(jv_data)
    with open(filename, "w") as jsonfile:
        json.dump(params, jsonfile)
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
