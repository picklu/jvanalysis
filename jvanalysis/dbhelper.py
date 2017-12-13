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
        fields = {}
        if salt and hashed:
            fields["salt"] = salt
            fields["hashed"] = hashed
        if email_confirmation_sent_on:
            fields["email_confirmation_sent_on"] = email_confirmation_sent_on
        if email_confirmed_on:
            fields["email_confirmed_on"] = email_confirmed_on
        if email_confirmed:
            fields["email_confirmed"] = email_confirmed
        self.db.users.update(where, {"$set": fields})
    
    def get_user(self, email):
        return self.db.users.find_one({"email": email})
    
    def upload_data(self, user_id, data):
        analyzed_on=datetime.datetime.utcnow()
        old_data = list(self.get_temporary_data(user_id))
        data_id = None
        if old_data:
            data_id = old_data[0]["_id"]
            self.db.tempdata.update({"_id": data_id, "user_id": user_id}, {"$set": {"analyzed_on": analyzed_on, "data": data}})
        else:
            data_id = self.db.tempdata.insert({"user_id": user_id, "analyzed_on": analyzed_on, "data": data})
        return data_id
    
    def get_temporary_data(self, user_id, data_id=None):
        if data_id:
            return self.db.tempdata.find_one({"_id": data_id, "user_id": user_id})
        else:
            return self.db.tempdata.find({"user_id": user_id})

    def delete_temporay_data(self, user_id):
        result = self.db.tempdata.remove({"user_id": user_id})
        return result["n"]
    
    def save_data(self, user_id, data_id):
        data = self.get_temporary_data(user_id, data_id)
        if data:
            self.delete_temporay_data(user_id)
            fields = {}
            fields["_id"] = data_id
            fields["user_id"] = user_id
            fields["analyzed_on"] = data["analyzed_on"]
            fields["data"] = data["data"]
            new_id = self.db.data.insert(fields)
            return new_id
    
    def get_data(self, user_id, data_id):
        return self.db.data.find_one({"user_id": user_id, "_id": data_id}, {"_id": 0, "data": 1})
        
    def get_all_data(self, user_id):
        data = list(self.db.data.find({"user_id": user_id}, 
            {"_id":1, "analyzed_on":1, "data.sample_name": 1, "data.area": 1, "data.temperature": 1}))
        return data
    
    def has_sample_name(self, user_id, sample_name):
        sample_name = list(self.db.data.find({"user_id": user_id, "data.sample_name": sample_name}, {"_id": 1}))
        return bool(sample_name)
    
    def get_data_count(self, user_id):
        data_count = len(self.get_all_data(user_id))
        return data_count
    
    def delete_data(self, user_id, data_id):
        result = self.db.data.remove({"user_id": user_id, "_id": data_id})
        return result["n"]