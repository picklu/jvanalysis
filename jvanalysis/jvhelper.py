# *********************************************
# source: http://flask.pocoo.org/snippets/106/
# *********************************************
from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId
from bson.errors import InvalidId

def mongo_id(text):
    "Return a mongodb _id as an ObjectId"
    return ObjectId(text)

def nice_id(object_id):
    "Convert a mongodb _id as a nice plain text"
    return base64_encode(str(object_id)).decode()

class ObjectIDConverter(BaseConverter):
    """ Based on the snippet found at flask.pocoo.org"""
    def to_python(self, value):
        try:
            return ObjectId(base64_decode(value).decode())
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()
    def to_url(self, value):
        return base64_encode(value.binary).decode()