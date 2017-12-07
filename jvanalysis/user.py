# *************************************************
# Modified from
# Book: Flask: Building Python Web Services
# By Gareth Dwyer, Shalabh Aggarwal, Jack Stouffer
# *************************************************
class User(object):
    def __init__(self, email):
        self.email = email
        self.id = ""
    
    def add_id(self, id):
        self.id = id
    
    def get_id(self):
        return self.id if self.id else self.email
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return True