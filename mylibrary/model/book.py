import datetime

from peewee import *

from mylibrary.routes import routes
from .base import BaseModel
from .user import UserModel

class BookModel(BaseModel):
    class Meta:
        table_name = "book"

    title = CharField()
    author = CharField()
    date_added = DateTimeField(default=datetime.datetime.utcnow)
    owner = ForeignKeyField(UserModel, backref='books')

    def as_dict(self, req):
        return {"title" : self.title,
            "author": self.author,
            "date_added": str(self.date_added),
            "owner": req.prefix + routes['user'].format(username_or_id=str(self.owner.id)),
            "href": req.prefix + routes['book'].format(id=str(self.id))
        }
