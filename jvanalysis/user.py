# *************************************************
# Modified from
# Book: Flask: Building Python Web Services
# By Gareth Dwyer, Shalabh Aggarwal, Jack Stouffer
# *************************************************
class User(object):
    def __init__(self, email):
        self.email = email
        self.id = None
        self.regular = True
        self.email_confirmed = False

    def get_id(self):
        return self.id if self.id else self.email

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True