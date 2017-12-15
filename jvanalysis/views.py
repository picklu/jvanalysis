from dateutil.parser import parse
from flask import make_response
from flask import render_template
from flask import json
from flask import request
from flask import redirect
from flask import session
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

from jvanalysis.jvplot import get_analyzed_params
from jvanalysis.jvplot import get_resources

from jvanalysis.user import User

if app.config.get("DATABASE"):
    from jvanalysis.dbhelper import DBHelper
else:
    from jvanalysis.mockdbhelper import MockDBHelper as DBHelper

from jvanalysis.passwordhelper import PasswordHelper

DB = DBHelper(app.config["DATABASE"])
PH = PasswordHelper()

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

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
    return render_template("about.html", next=next, 
                            signin_form=form, title="About")


@app.route("/how")
def how():
    next = get_redirect_target()
    return render_template("how.html", next=next, title="How")

@app.route("/account")
@login_required
def account():
    next = get_redirect_target()
    guest_email = app.config['GUEST_USER_EMAIL']
    regular = not guest_email == current_user.email
    user_id = mongo_id(current_user.id)
    saved_data = DB.get_all_data(user_id)
    return render_template("account.html", next=next, 
                            saved_data=saved_data, regular=regular, 
                            title="Account")


@app.route("/plot/<string:data_type>/<objectid:data_id>")
@login_required
def plot(data_type, data_id):
    user_id = mongo_id(current_user.id)
    if data_type == "persistent":
        data = DB.get_data(user_id, data_id)
    elif data_type == "temporary":
        session_id = mongo_id(session["sid"])
        data = DB.get_temporary_data(user_id, session_id, data_id)

    if data:
        bkdiv, bkscript = get_resources(data["data"])
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
    form = request.form
    area = float(form["area"])
    data = form["jv"]
    sample_name = form["sample-name"]
    measured_on = parse(form["measured-date"], dayfirst=True)
    temperature = float(form.get("temperature"))
    jv = json.loads(data)
    params = get_analyzed_params(jv, area, temperature)
    if params:
        params.update({
            "area": area,
            "measured_on": measured_on,
            "sample_name": sample_name,
            "temperature": temperature
        })
        user_id = mongo_id(current_user.id)
        session_id = mongo_id(session["sid"])
        data_count = DB.get_data_count(user_id)
        data_id = DB.upload_data(user_id, session_id, params)
        if data_id:
            params["data_id"] = nicefy(data_id)
            if data_count < 4:
                params["success"] = "Data were uploaded and analyzed successfully! You may save the data to your account."
                return json.dumps(params)
            else:
                params["warning"] = """Data were uploaded and analyzed successfully!
                                    However, you can't save the data to your account since you have already saved five data."
                                    You may navigate to your account to see your saved data."""
                return json.dumps(params)
        return json.dumps({
            "fail": "Failed to save data to the temporary database."
        })
    return json.dumps({
        "fail": "Failed to analyze data. Please check if the data headers have been identified correctly."
    })


@app.route("/result", methods=["POST"])
@login_required
def result():
    user_id = mongo_id(current_user.id)
    data_id = request.form.get("data_id")
    action = request.form.get("action")
    
    if data_id:
        data_id = mongo_id(data_id)
    else:
        return json.dumps({"fail": "Invalid request."})
    
    if action == "view":
            data = DB.get_data(user_id, data_id)
            if data:
                params = data["data"]
                params["success"] = "Successfully retrieved the data."
                return json.dumps(params)
            return json.dumps({
                "fail": "Failed to retrieve data from the database."
            })
        
    elif action == "delete":
        deleted = DB.delete_data(user_id, data_id)
        if deleted:
            return json.dumps({
                "success": "Successfully deleted the data."
            })
        return json.dumps({
            "fail": "Failed to delete the data from the database."
        })


@app.route("/save", methods=["POST"])
@login_required
def save():
    user_id = mongo_id(current_user.id)
    data_count = DB.get_data_count(user_id)
    result = {}
    if data_count >= 5:
        result["fail"] = "Sorry! You can't save more than five analyzed data at the moment."
        return json.dumps(result)
    else:
        data_id = mongo_id(request.form.get("data_id"))
        session_id = mongo_id(session["sid"])
        new_id = DB.save_data(user_id, session_id, data_id)
        if new_id:
            result["success"] = "The analyzed data were saved successfully! You may see the saved data by navigating to your account."
            return json.dumps(result)
        result["fail"] = "Failed to save the analyzed data."
        return json.dumps(result)


@app.route("/analysis")
@login_required
def analysis():
    next = get_redirect_target()
    return render_template("analysis.html", next=next, title="Analysis")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template(
            "signup.html", signup_form=SignupForm(), title="Sign Up")
    form = SignupForm(request.form)
    if form.validate():
        email = form.email.data
        if DB.get_user(email):
            form.email.errors.append("Email address already registered")
            return render_template("signup.html", signup_form=form)
        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data, salt, hashed)
        messages = json.dumps({
            "message": "Sign up successful! Please sign in.",
            "id": email
        })
        return redirect(url_for("signin", success=nicefy(messages)))
    return render_template("signup.html", signup_form=form)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    next = get_redirect_target()
    # if the requested method is GET
    if request.method == "GET":
        form = SigninForm()
        success = request.args.get("success")
        if success:
            messages = json.loads(uglyfy(success))
            form.message = messages["message"]
            form.email.data = messages["id"]
        return render_template("signin.html", next=next, 
                                signin_form=form, title="Sign In")
    # else the method must be post
    form = SigninForm(request.form)
    if form.validate():
        db_user = DB.get_user(form.email.data)
        if db_user:
            if PH.validate_password(form.password.data, db_user['salt'],
                                    db_user['hashed']):
                user = User(db_user["email"])
                login_user(user, remember=True)
                session["sid"] = nicefy(mongo_id())
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
    user_id = mongo_id(current_user.id)
    session_id = mongo_id(session["sid"])
    DB.delete_temporay_data(user_id, session_id)
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
            session['sid'] = nicefy(mongo_id())
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
    return render_template("data.html", sample_data=sample_data, 
                            title="Sample Data")


@app.route("/validator")
@login_required
def validator():
    user_id = mongo_id(current_user.id)
    sample_name = request.args.get("sample-name")
    used_name = DB.has_sample_name(user_id, sample_name)
    if used_name:
        message = "Name already exists!"
        status = 400
    else:
        message = "It's a new name!"
        status = 200
    resp = make_response(message, status)
    resp.headers["X-data-name-validator"] = message
    return resp