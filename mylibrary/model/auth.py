from .user import UserModel
from peewee import DoesNotExist

def authenticate(username, password):
    try:
        user = UserModel.get(UserModel.username == username)
        if user.password == password:
            return {'username': username,
            'id': user.id,
            'is_admin': username == 'admin'}
    except DoesNotExist:
        pass
    return None
