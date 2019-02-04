import datetime

from peewee import *

from mylibrary.routes import routes

from .base import BaseModel
from .book import BookModel
from .user import UserModel

class LoanModel(BaseModel):
    class Meta:
        table_name = "loan"

    book = ForeignKeyField(BookModel, backref='loans')
    owner = ForeignKeyField(UserModel)
    borrower = ForeignKeyField(UserModel, backref='borrows')
    date_borrowed = DateTimeField(default=datetime.datetime.utcnow)
    date_due = DateTimeField()
    date_returned = DateTimeField(null=True)

    def as_dict(self, req):
        return {"book" : req.prefix + routes['book'].format(id=str(self.book.id)),
            "owner": req.prefix + routes['user'].format(username_or_id=str(self.book.owner.id)),
            "borrower": req.prefix + routes['user'].format(username_or_id=str(self.borrower.id)),
            "date_borrowed": str(self.date_borrowed),
            "date_due": str(self.date_due),
            "date_returned": str(self.date_returned)
        }
