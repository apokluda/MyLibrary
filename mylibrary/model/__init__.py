from peewee import IntegrityError

from mylibrary import db

from .user import UserModel
from .book import BookModel
from .loan import LoanModel

db.create_tables([UserModel, BookModel, LoanModel])

# Create the admin user
admin_user = UserModel(username='admin',password='passw0rd')
try:
    admin_user.save()
except IntegrityError:
    pass # Admin user already exists
