import json
import uuid
from flask_login import UserMixin

USER_FILE = 'users.json'

class User(UserMixin):
    def __init__(self, id, username, password, registration_token=None, registered=False):
        self.id = id
        self.username = username
        self.password = password
        self.registration_token = registration_token
        self.registered = registered

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "registration_token": self.registration_token,
            "registered": self.registered
        }

def load_users():
    with open(USER_FILE, 'r') as f:
        users_data = json.load(f)
    return [User(**user) for user in users_data]

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump([user.to_dict() for user in users], f, indent=4)

def get_user_by_username(username):
    users = load_users()
    for user in users:
        if user.username == username:
            return user
    return None

def get_user_by_id(user_id):
    users = load_users()
    for user in users:
        if user.id == user_id:
            return user
    return None

def get_user_by_token(token):
    users = load_users()
    for user in users:
        if user.registration_token == token:
            return user
    return None

def add_user(username):
    users = load_users()
    user_id = max(user.id for user in users) + 1
    token = str(uuid.uuid4())
    new_user = User(id=user_id, username=username, password='', registration_token=token)
    users.append(new_user)
    save_users(users)
    return token

def update_user(user):
    users = load_users()
    for i, u in enumerate(users):
        if u.id == user.id:
            users[i] = user
            break
    save_users(users)
