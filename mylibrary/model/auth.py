from .user import UserModel
from peewee import DoesNotExist

def authenticate(username, password):
    try:
        user = UserModel.get(UserModel.username == username)
        if user.password == password:
            # In this exercise, the user's plaintext password is stored in the
            # user table. In a real implementation, we would shore hashed
            # passwords in their own isolated DB with another REST API for
            # authentication. Regardless, let's clear the password anyway :)
            user.password = None
            return user
    except DoesNotExist:
        pass
    return None
