# *************************************************
# Book: Flask: Building Python Web Services
# By Gareth Dwyer, Shalabh Aggarwal, Jack Stouffer
# *************************************************
import pymongo
import datetime
from jvanalysis import app

DATABASE = app.config["DATABASE"]


class DBHelper(object):
    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client[DATABASE]

    def add_user(self,
                 email,
                 salt=None,
                 hashed=None,
                 signedup_on=datetime.datetime.utcnow(),
                 email_confirmation_sent_on=datetime.datetime.utcnow(),
                 email_confirmed_on=None,
                 email_confirmed=False):
        self.db.users.insert({
            "email": email,
            "salt": salt,
            "hashed": hashed,
            "signedup_on": datetime.datetime.utcnow(),
            "email_confirmation_sent_on": email_confirmation_sent_on,
            "email_confirmed_on": email_confirmed_on,
            "email_confirmed": email_confirmed
        })

    def update_user(self,
                    email,
                    salt=None,
                    hashed=None,
                    signedup_on=datetime.datetime.utcnow(),
                    email_confirmation_sent_on=datetime.datetime.utcnow(),
                    email_confirmed_on=None,
                    email_confirmed=False):
        where = {"email": email}
        query = {}
        if salt and hashed:
            query["salt"] = salt
            query["hashed"] = hashed
        if email_confirmation_sent_on:
            query["email_confirmation_sent_on"] = email_confirmation_sent_on
        if email_confirmed_on:
            query["email_confirmed_on"] = email_confirmed_on
        if email_confirmed:
            query["email_confirmed"] = email_confirmed
        self.db.users.update(where, {"$set": query})
    
    def get_user(self, email):
        return self.db.users.find_one({"email": email})
    
    def upload_data(self, user_id, data):
        old_data = list(self.db.tempdata.find({"user_id": user_id}, {"_id": 1}))
        if old_data:
            print(old_data)
            data_id = old_data[0]["_id"]
            self.db.tempdata.update({"_id": data_id, "user_id": user_id}, {"$set": {"data": data}})
        else:
            data_id = self.db.tempdata.insert({"user_id": user_id, "data": data})
        return data_id
    
    def get_temporary_data(self, user_id, data_id):
        return self.db.tempdata.find_one({"_id": data_id, "user_id": user_id}, {"_id": 0, "data": 1})

    def delete_temporay_data(self, data_id, user_id):
        self.db.tempdata.remove({"_id": data_id, "user_id": user_id})
    
    def save_data(self, user_id, data_id):
        data = self.get_temporary_data(data_id, user_id)
        new_id = self.db.tempdata.insert({"user_id": user_id, "data_id": data_id, "data": data})
        return new_id
    
    def get_data(self, user_id, data_id):
        return self.db.data.find_one({"user_id": user_id, "data_id": data_id})
        
    def get_all_data(self, user_id):
        data = list(self.db.data.find({"user_id": user_id}, {"_id": 0, "data": 1}))
        return data