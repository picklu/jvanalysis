import urllib.request
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import redirect, request, url_for
from itsdangerous import base64_encode, base64_decode
from urllib.parse import urlparse, urljoin
from werkzeug.routing import BaseConverter, ValidationError

def mongo_id(nice_id=None):
    "Return a mongodb _id as an ObjectId"
    if nice_id:
        return ObjectId(uglyfy(nice_id))
    return ObjectId()

def nicefy(uglytext):
    "Convert a mongodb _id as a nice plain text"
    return base64_encode(str(uglytext)).decode()

def uglyfy(nicetext):
    "Convert a nice plain text to its original form"
    return base64_decode(nicetext).decode()

def nice_date(date):
    return date.strftime("%Y/%m/%d")

def nice_number(number, sd=2):
    return "{0:0.{1:d}f}".format(number, sd)

# *********************************************
# Modified from
# ource: http://flask.pocoo.org/snippets/62/
# *********************************************
def is_safe_url(target):
    """ return True if the target is safe; false otherwise"""
    if target == "index": return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

# *********************************************
# Modified from
# ource: http://flask.pocoo.org/snippets/62/
# *********************************************
def get_redirect_target():
    """ return target url

    From Securely Redirect Back. source: http://flask.pocoo.org/snippets/62/
    """
    target = request.endpoint
    bad_endpoints = ["account", "analysis", "how", "signin", "signout"]
    if is_safe_url(target):
        if any(suburl in target for suburl in bad_endpoints):
            return url_for("index")
        return target
    return url_for("index")

# *********************************************
# Modified from
# ource: http://flask.pocoo.org/snippets/62/
# *********************************************
def redirect_back(endpoint, **values):
    """ redirect url back to the referrer

    From Securely Redirect Back. source: http://flask.pocoo.org/snippets/62/
    """
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

# *********************************************
# Modified from
# source: http://flask.pocoo.org/snippets/106/
# *********************************************
class ObjectIDConverter(BaseConverter):
    """ Based on the snippet found at flask.pocoo.org"""
    def to_python(self, value):
        try:
            return ObjectId(base64_decode(value).decode())
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()
    def to_url(self, value):
        return base64_encode(value.binary).decode()