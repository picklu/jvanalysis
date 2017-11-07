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
    bkjs = INLINE.render_js()
    bkcss = INLINE.render_css()
    div, script = resources()
    div1, script1 = resources(300, 300)
    div2, script2 = resources(300, 300)
    return render_template("dashboard.html", div=div, div1=div1, div2=div2,
                            script=script, script1=script1, script2=script2,
                            bokehjs=bkjs, bokehcss=bkcss, title="Dashboard")

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