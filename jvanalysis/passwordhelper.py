# *************************************************
# Modified from
# Book: Flask: Building Python Web Services
# By Gareth Dwyer, Shalabh Aggarwal, Jack Stouffer
# *************************************************
import os
from base64 import b64encode
from hashlib import sha512


class PasswordHelper(object):
    def get_hash(self, plain):
        return sha512(plain.encode('utf-8')).hexdigest()

    def get_salt(self):
        return b64encode(os.urandom(20)).decode()

    def validate_password(self, plain, salt, expected):
        return self.get_hash(plain + salt) == expected
