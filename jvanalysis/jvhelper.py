# *********************************************
# source: http://flask.pocoo.org/snippets/106/
# *********************************************
from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId
from bson.errors import InvalidId

def mongo_id(text):
    "Return mongodb _id as ObjectId"
    return ObjectId(text)

def nice_id(text):
    "Convert mongodb _id string as nice text"
    return base64_encode(text).decode()

class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(base64_decode(value).decode())
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()
    def to_url(self, value):
        return base64_encode(value.binary).decode()