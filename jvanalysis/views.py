from flask import render_template
from flask import json
from flask import request
from flask import redirect
from flask import url_for

from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from jvanalysis import app
from jvanalysis import login_manager

from jvanalysis.forms import SigninForm
from jvanalysis.forms import SignupForm

from jvanalysis.jvhelper import get_redirect_target
from jvanalysis.jvhelper import mongo_id
from jvanalysis.jvhelper import nicefy
from jvanalysis.jvhelper import redirect_back
from jvanalysis.jvhelper import is_safe_url
from jvanalysis.jvhelper import uglyfy

from jvanalysis.jvplot import resources
from jvanalysis.jvplot import get_params
from jvanalysis.jvplot import get_resources

from jvanalysis.user import User

if app.config.get("DATABASE"):
    from jvanalysis.dbhelper import DBHelper
else:
    from jvanalysis.mockdbhelper import MockDBHelper as DBHelper

from jvanalysis.passwordhelper import PasswordHelper

DB = DBHelper()
PH = PasswordHelper()

@login_manager.user_loader
def load_user(email):
    guest_email = app.config['GUEST_USER_EMAIL']
    db_user = DB.get_user(email)
    if db_user:
        id = nicefy(db_user["_id"])
        user = User(email)
        user.id = id
        if email == guest_email:
            user.regular = False
        return user

@login_manager.unauthorized_handler
def unauthorized_callback():
    message = nicefy("""Your are not signed in! 
        Plase sign in to get full access. 
        If you are here for the first time then, please, 
        sign up or you may try as a guest after closing this warning.""")
    return redirect(url_for('index', message=message))

@app.route("/")
def index():
    next = get_redirect_target()
    if current_user.is_authenticated:
        return render_template("home.html", next=next)
    else:
        form = SigninForm()
        message = request.args.get("message")
        if message:
            form.message = uglyfy(message)
        return render_template("home.html", next=next, signin_form=form)

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

@app.route("/plot/<string:data_type>/<objectid:data_id>")   
@login_required
def plot(data_type, data_id):
    user_id = mongo_id(current_user.id)
    if data_type == "persistent":
        data = DB.get_data(user_id, data_id).get("data")
    elif data_type == "temporary":
        data = DB.get_temporary_data(user_id, data_id).get("data")
    
    if data:
        bkdiv, bkscript = get_resources("jV plot of analyzed data", data)
        return render_template(
            "plot.html",
            bkdiv=bkdiv,
            bkscript=bkscript,
            title="plot|" + nicefy(data_id) if data_id else "plot")
    else:
        return json.dumps({"error": "Data not found!"})

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    data = request.form.get("jv")
    jv_data = json.loads(data)
    params = get_params(jv_data)
    if params:
        user_id = mongo_id(current_user.id)
        data_id = DB.upload_data(user_id, params)
        if data_id:
            params["data_id"] = nicefy(data_id)
            params["success"] = "Data were uploaded and analyzed successfully!"
            return json.dumps(params)
        return json.dumps({"fail": "Failed to save data to the temporary database."})
    return json.dumps({"fail": "Failed to analyze data. Please check if the data headers have been identified correctly."})

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
        return redirect(url_for("signin", success=nicefy(messages)))
    return render_template("signup.html", signup_form=form)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    next = get_redirect_target()
    # if the requested method is GET
    if request.method == "GET":
        form=SigninForm()
        success = request.args.get("success")
        if success:
            messages = json.loads(uglyfy(success))
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
def guest():
    email = app.config['GUEST_USER_EMAIL']
    password = app.config['GUEST_USER_PASSWORD']
    db_user = DB.get_user(email)
    if db_user:
        if PH.validate_password(password, db_user['salt'], db_user['hashed']):
            user = User(db_user["email"])
            login_user(user, remember=True)
            return redirect(url_for("analysis"))
    else:    
        message = nicefy("There is no guest access at the moment!")
        return redirect(url_for('index', message=message))

@app.route("/data/<path:path>")
@login_required
def data(path):
    file_name = app.config['SAMPLE_DATA']
    sample_data = "No data found!"
    if file_name == path:
        file_path = "data/" + file_name
        with open(file_path, "r") as f:
            sample_data = f.read()
    return render_template("data.html", sample_data=sample_data, title="Sample Data")