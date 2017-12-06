# *************************************************
# Modified from
# Book: Flask: Building Python Web Services
# By Gareth Dwyer, Shalabh Aggarwal, Jack Stouffer
# *************************************************
class User(object):
    def __init__(self, email, id, active=True):
        self.email = email
        self.id = id
        self.active = active
    
    def get_email(self):
        return self.email
    
    def get_id(self):
        return self.id
    
    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return True