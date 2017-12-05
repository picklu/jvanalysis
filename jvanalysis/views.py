from flask import render_template
from flask import request
from flask import json
from flask import url_for

from jvanalysis import app
from jvanalysis.jvplot import DATA_FOLDER
from jvanalysis.jvplot import resources
from jvanalysis.jvplot import get_params
from jvanalysis.jvplot import get_resources
if app.config.get('TESTING'):
    from jvanalysis.mockdbhelper import MockDBHelper as DBHelper
else:
    from jvanalysis.dbhelper import DBHelper
from jvanalysis.passwordhelper import PasswordHelper

DB = DBHelper()
PH = PasswordHelper()

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

@app.route("/plot/<data_id>")
def plot(data_id):
    if data_id:
        data_id = int(data_id)
        user_id = 1
        data = DB.get_data(user_id, data_id)
        bkdiv, bkscript = get_resources("jV plot of analyzed data", data)
    else:
        bkdiv, bkscript = resources("jV Plot")
    return render_template(
        "plot.html",
        bkdiv=bkdiv,
        bkscript=bkscript,
        title="plot|" + data_id if data_id else "plot")

@app.route("/upload", methods=["POST"])
def upload():
    data = request.form.get("jv")
    jv_data = json.loads(data)
    params = get_params(jv_data)
    id = DB.add_data(1, params)
    params["data_id"] = id
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
