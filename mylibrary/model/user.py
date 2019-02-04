import datetime

from peewee import *

from mylibrary.routes import routes
from .base import BaseModel

def is_admin(user):
    return user.username == "admin"

# NOTE: This is just an exercise. In a real implementation we would never store
#       a plain text password!

class UserModel(BaseModel):
    class Meta:
        table_name = "user"

    username = CharField(unique=True)
    password = CharField()
    join_date = DateTimeField(default=datetime.datetime.utcnow)

    def as_dict(self, req, include_books=False):
        dict = {"id": self.id,
            "username" : self.username,
            "join_date": str(self.join_date),
            "href": req.prefix + routes['user'].format(username_or_id=str(self.id))
        }
        if include_books:
            dict["books"] = [req.prefix + routes['book'].format(id=str(book.id)) for book in self.books]
        return dict
