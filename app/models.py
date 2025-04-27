from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from .extensions import mongo  # Now coming from extensions
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.password_hash = user_data["password"]

    @staticmethod
    def get_by_id(user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    @staticmethod
    def get_by_username(username):
        user_data = mongo.db.users.find_one({"username": username})
        return User(user_data) if user_data else None

    @staticmethod
    def create_user(username, password):
        existing = mongo.db.users.find_one({"username": username})
        if existing:
            return None
        hashed_password = generate_password_hash(password)
        user_id = mongo.db.users.insert_one({
            "username": username,
            "password": hashed_password
        }).inserted_id
        return User.get_by_id(user_id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message:
    def __init__(self, mongo):
        self.collection = mongo.db.messages

    def save_message(self, room, sender, content, edited=False):
        message = {
            "room": room,
            "sender": sender,
            "content": content,
            "timestamp": datetime.utcnow(),
            "edited": edited
        }
        result = self.collection.insert_one(message)  # result is InsertOneResult
        return str(result.inserted_id)  # Ensure that it's a string representation of ObjectId

    def get_messages(self, room, limit=50):
        messages = list(self.collection.find({"room": room}).sort("timestamp", -1).limit(limit))
        return messages[::-1]  # now this works as expected

    def update_message(self, message_id, new_content):
        self.collection.update_one(
            {"_id": ObjectId(message_id)},
            {
                "$set": {
                    "content": new_content,
                    "edited": True,
                    "timestamp": datetime.utcnow()  # optional: update timestamp
                }
            }
        )

    def delete_message(self, message_id):
        return self.collection.delete_one({"_id": ObjectId(message_id)})
    
    def is_owner(self, msg_id, username):
        msg = self.collection.find_one({"_id": ObjectId(msg_id)})
        return msg and msg["sender"] == username
    
    def get_messages_by_room(self, room):
        return list(self.collection.find({"room": room}).sort("timestamp", 1))


