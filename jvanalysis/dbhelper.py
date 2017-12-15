# *************************************************
# Book: Flask: Building Python Web Services
# By Gareth Dwyer, Shalabh Aggarwal, Jack Stouffer
# *************************************************
from datetime import datetime
from flask_pymongo import MongoClient

class DBHelper(object):
    def __init__(self, db):
        client = MongoClient()
        self.client = client
        self.users = client[db]['users']
        self.data = client[db]['data']
        self.tempdata = client[db]['tempdata']

    def add_user(self, email, salt=None, hashed=None,
                 signedup_on=datetime.utcnow(),
                 email_confirmation_sent_on=datetime.utcnow(),
                 email_confirmed_on=None,
                 email_confirmed=False):
        return self.users.insert({
            "email": email,
            "salt": salt,
            "hashed": hashed,
            "signedup_on": datetime.utcnow(),
            "email_confirmation_sent_on": email_confirmation_sent_on,
            "email_confirmed_on": email_confirmed_on,
            "email_confirmed": email_confirmed
        })
        

    def update_user(self, email, salt=None, hashed=None, 
                    signedup_on=datetime.utcnow(),
                    email_confirmation_sent_on=datetime.utcnow(),
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
        return self.users.update(where, {"$set": fields})
    
    def get_user(self, email):
        return self.users.find_one({"email": email})
    
    def upload_data(self, user_id, sid, data):
        data["analyzed_on"] = datetime.utcnow()
        old_data = self.get_temporary_data(user_id, sid)
        data_id = None
        if old_data:
            data_id = old_data[0]["_id"]
            self.tempdata.update({"_id": data_id, "user_id": user_id, "sid": sid}, {"$set": {"data": data}})
        else:
            data_id = self.tempdata.insert({"user_id": user_id, "sid": sid, "data": data})
        return data_id
    
    def get_temporary_data(self, user_id, sid, data_id=None):
        if data_id:
            return self.tempdata.find_one({"_id": data_id, "user_id": user_id, "sid": sid})
        else:
            return list(self.tempdata.find({"user_id": user_id, "sid": sid}))

    def delete_temporay_data(self, user_id, sid):
        result = self.tempdata.remove({"user_id": user_id, "sid": sid})
        return result["n"]
    
    def save_data(self, user_id, sid, data_id):
        data = self.get_temporary_data(user_id, sid, data_id)
        if data:
            self.delete_temporay_data(user_id, sid)
            fields = {}
            fields["_id"] = data_id
            fields["user_id"] = user_id
            fields["data"] = data["data"]
            new_id = self.data.insert(fields)
            return new_id
    
    def get_data(self, user_id, data_id):
        return self.data.find_one({"user_id": user_id, "_id": data_id}, {"_id": 0, "data": 1})
        
    def get_all_data(self, user_id):
        data = list(self.data.find({"user_id": user_id}, 
            {"_id":1, "data.analyzed_on":1, "data.sample_name": 1, "data.area": 1, "data.temperature": 1}))
        return data
    
    def has_sample_name(self, user_id, sample_name):
        sample_name = list(self.data.find({"user_id": user_id, "data.sample_name": sample_name}, {"_id": 1}))
        return bool(sample_name)
    
    def get_data_count(self, user_id):
        data_count = len(self.get_all_data(user_id))
        return data_count
    
    def delete_data(self, user_id, data_id):
        result = self.data.remove({"user_id": user_id, "_id": data_id})
        return result["n"]