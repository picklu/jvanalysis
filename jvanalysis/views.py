from flask import render_template
from flask import json
from flask import request
from flask import redirect
from flask import url_for

from flask_login import current_user
from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from jvanalysis import app
from flask_login import LoginManager

from jvanalysis.forms import SigninForm
from jvanalysis.forms import SignupForm

from jvanalysis.jvhelper import mongo_id
from jvanalysis.jvhelper import nice_id

from jvanalysis.jvplot import DATA_FOLDER
from jvanalysis.jvplot import resources
from jvanalysis.jvplot import get_params
from jvanalysis.jvplot import get_resources

from jvanalysis.user import User

if app.config.get('TESTING'):
    from jvanalysis.mockdbhelper import MockDBHelper as DBHelper
else:
    from jvanalysis.dbhelper import DBHelper

from jvanalysis.passwordhelper import PasswordHelper

DB = DBHelper()
PH = PasswordHelper()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        email = user_password["email"]
        id = nice_id(user_password["_id"])
        return User(email, id)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('index'))

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return render_template("home.html", signin_form=SigninForm())

@app.route("/home")
@login_required
def home():
    return render_template("home_secured.html")

@app.route("/about")
@login_required
def about():
    return render_template("about.html", title="About")

@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")

@app.route("/plot/<objectid:data_id>")   
@login_required
def plot(data_id):
    try:
        user_id = current_user.get_id()
        data = DB.get_data(user_id, data_id).get("data")
        bkdiv, bkscript = get_resources("jV plot of analyzed data", data)
        return render_template(
            "plot.html",
            bkdiv=bkdiv,
            bkscript=bkscript,
            title="plot|" + str(data_id) if data_id else "plot")
    except:
        return json.dumps({"error": "Invalid Data ID!"})

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    data = request.form.get("jv")
    jv_data = json.loads(data)
    params = get_params(jv_data)
    id = DB.add_data(current_user.id, params)
    params["data_id"] = nice_id(id)
    return json.dumps(params)

@app.route("/analysis")
@login_required
def analysis():
    return render_template("analysis.html", title="Analysis")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", signup_form=SignupForm(), title="Sign Up")
    form = SignupForm(request.form)
    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append("Email address already registered")
            return render_template("signup.html", signup_form=form)
        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data, salt, hashed)
        return render_template("home.html", onloadmessage="Registration successful. Please log in.")
    return render_template("signup.html", signup_form=form)



@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html", signin_form=SigninForm(), title="Sign In")
    form = SigninForm(request.form)
    if form.validate():
        db_user = DB.get_user(form.email.data)
        if db_user:
            if PH.validate_password(form.password.data, db_user['salt'], db_user['hashed']):
                email = db_user["email"]
                id = nice_id(db_user["_id"])
                user = User(email, id)
                login_user(user, remember=True)
                return redirect(url_for("home"))
            else:
                form.email.errors = []
                form.password.errors.append("Invalid password")
        else:    
            form.email.errors.append("Email is not found")
    return render_template("signin.html", signin_form=form)

@app.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/guest")
@login_required
def guest():
    return home()