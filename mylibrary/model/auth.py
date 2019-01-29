from .user import UserModel
from peewee import DoesNotExist

def authenticate(username, password):
    try:
        user = UserModel.get(UserModel.username == username)
        return {"username": username} if user.password == password else None
    except DoesNotExist:
        return None
