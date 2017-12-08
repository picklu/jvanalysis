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

from jvanalysis.jvhelper import get_redirect_target
from jvanalysis.jvhelper import mongo_id
from jvanalysis.jvhelper import nice_id
from jvanalysis.jvhelper import redirect_back
from jvanalysis.jvhelper import is_safe_url
from jvanalysis.jvhelper import ugly_id

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
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(email):
    db_user = DB.get_user(email)
    if db_user:
        id = nice_id(db_user["_id"])
        user = User(email)
        user.add_id(id)
        return user

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('index'))

@app.route("/")
def index():
    next = get_redirect_target()
    if current_user.is_authenticated:
        return render_template("home_secured.html", next=next)
    else:
        return render_template("home.html", next=next, signin_form=SigninForm())

@app.route("/about")
def about():
    next = get_redirect_target()
    if current_user.is_authenticated:
        form = None
    else:
        form = SigninForm()
    return render_template("about.html", next=next, signin_form=form, title="About")

@app.route("/account")
@login_required
def account():
    next = get_redirect_target()
    return render_template("account.html", next=next, title="Account")

@app.route("/plot/<objectid:data_id>")   
@login_required
def plot(data_id):
    try:
        user_id = current_user.id
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
    next = get_redirect_target()
    return render_template("analysis.html", next=next, title="Analysis")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", signup_form=SignupForm(), title="Sign Up")
    form = SignupForm(request.form)
    if form.validate():
        email = form.email.data
        if DB.get_user(email):
            form.email.errors.append("Email address already registered")
            return render_template("signup.html", signup_form=form)
        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data, salt, hashed)
        messages = json.dumps({"message": "Sign up successful! Please sign in.", 
                                "id": email})
        return redirect(url_for("signin", success=nice_id(messages)))
    return render_template("signup.html", signup_form=form)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    next = get_redirect_target()
    # if the requested method is GET
    if request.method == "GET":
        form=SigninForm()
        success = request.args.get("success")
        if success:
            messages = json.loads(ugly_id(success))
            form.message = messages["message"]
            form.email.data = messages["id"]
        return render_template("signin.html", next=next, signin_form=form, title="Sign In")
    # else the method must be post 
    form = SigninForm(request.form)
    if form.validate():
        db_user = DB.get_user(form.email.data)
        if db_user:
            if PH.validate_password(form.password.data, db_user['salt'], db_user['hashed']):
                user = User(db_user["email"])
                login_user(user, remember=True)
                return redirect_back("index")
            else:
                form.email.errors = []
                form.password.errors.append("Invalid password")
        else:    
            form.email.errors.append("Email not found")
    return render_template("signin.html", next=next, signin_form=form)

@app.route("/signout", methods=["POST"])
@login_required
def signout():
    logout_user()
    return redirect_back("index")

@app.route("/guest")
@login_required
def guest():
    return index()