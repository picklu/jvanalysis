import urllib.request
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import request
from itsdangerous import base64_encode, base64_decode
from urllib.parse import urlparse, urljoin
from werkzeug.routing import BaseConverter, ValidationError

def mongo_id(text):
    "Return a mongodb _id as an ObjectId"
    return ObjectId(text)

def nice_id(object_id):
    "Convert a mongodb _id as a nice plain text"
    return base64_encode(str(object_id)).decode()

def ugly_id(nice_id):
    "Convert a nice plain text to its original form"
    return base64_decode(nice_id).decode()

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