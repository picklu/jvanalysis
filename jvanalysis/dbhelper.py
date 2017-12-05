import pymongo

DATABASE = "jvanalysis"


class DBHelper(object):

    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client[DATABASE]
    
    def get_user(self, email):
        return self.db.users.find_one({"email": email})

    def add_user(self, email, salt, hashed):
        self.db.users.insert({"email": email, "salt": salt, "hashed": hashed})
    
    def add_data(self, user_id, data):
        new_id = self.db.data.insert({"user_id": user_id, "data": data})
        return str(new_id)

    def get_data(self, user_id, data_id):
        return self.db.data.find_one({"_id": data_id, "user_id": user_id})
    
    def get_all_data(self, user_id):
        data = list(self.db.data.find({"user_id": user_id}))
        return data
        
    def delete_data(self, data_id):
        self.db.data.remove({"_id": data_id})