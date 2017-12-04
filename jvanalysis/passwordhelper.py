import base64
import hashlib
import os

class PasswordHelper(object):

    def get_hash(self, plain):
        return hashlib.sha512(plain.encode('utf-8')).hexdigest()

    def get_salt(self):
        return base64.b64encode(os.urandom(20)).decode()

    def validate_password(self, plain, salt, expected):
        return self.get_hash(plain + salt) == expected