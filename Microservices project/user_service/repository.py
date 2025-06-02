# user_service/repository.py
from pymongo import MongoClient

client = MongoClient("mongodb://mongo1:27017,mongo2:27018/?replicaSet=rs0")
db = client.userdb

class UserRepository:
    @staticmethod
    def add_user(data):
        result = db.users.insert_one(data)
        return {"user_id": str(result.inserted_id)}
