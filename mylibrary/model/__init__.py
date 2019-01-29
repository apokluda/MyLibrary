from mylibrary import db

from .user import UserModel

db.create_tables([UserModel])
