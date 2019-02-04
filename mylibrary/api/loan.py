import falcon
from falcon.media.validators import jsonschema

from peewee import *

import mylibrary.model.book
import mylibrary.model.user
from mylibrary.model.book import BookModel
from mylibrary.model.loan import LoanModel, DoesNotExist
from mylibrary.model.user import UserModel, is_admin

from mylibrary.routes import routes
import mylibrary.schemas as schemas

class Loans(object):
    def on_get(self, req, resp):
        auth_user = req.context['user']
        if is_admin(auth_user):
            loans = LoanModel.select()
        else:
            loans = LoanModel.select().where((LoanModel.owner == auth_user) |
                (LoanModel.borrower == auth_user))

        resp.media = {
            "href": req.uri,
            "items": [loan.as_dict(req) for loan in loans]
        }

    @jsonschema.validate(schemas.create_loan)
    def on_post(self, req, resp):
        doc = req.media
        try:
            book = BookModel.get(BookModel.id == int(doc.get('book_id')))
        except mylibrary.model.book.DoesNotExist:
            raise falcon.HTTPNotFonud(
                description="The requested book does not exist."
            )

        auth_user = req.context['user']
        if not book.owner.id == auth_user.id:
            raise falcon.HTTPUnauthorized(
                "Operation Not Permitted",
                "You cannot loan out other users' books."
            )

        try:
            borrower = UserModel.get(UserModel.id == int(doc.get('user_id')))
        except mylibrary.model.user.DoesNotExist:
            raise falcon.HTTPNotFonud(
                description="The requested borrower does not exist."
            )

        loan = LoanModel(
            book=book,
            owner=auth_user,
            borrower=borrower,
            date_due=doc.get('date_due')
        )

        loan.save()
        resp.status = falcon.HTTP_CREATED
        resp.location = routes['loan'].format(id=loan.id)
