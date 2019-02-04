import falcon
from falcon.media.validators import jsonschema

from peewee import *

from mylibrary.model.book import BookModel, DoesNotExist

from mylibrary.routes import routes
import mylibrary.schemas as schemas

class Books(object):
    def on_get(self, req, resp):
        resp.media = {
            "href": req.uri,
            "items": [book.as_dict(req) for book in BookModel.select()]
        }

    @jsonschema.validate(schemas.create_book_schema)
    def on_post(self, req, resp):
        doc = req.media
        book = BookModel(
            title=doc.get('title'),
            author=doc.get('author'),
            owner=req.context['user']
        )
        book.save()
        resp.status = falcon.HTTP_CREATED
        resp.location = routes['book'].format(id=book.id)

class Book(object):
    def on_get(self, req, resp, username_or_id):
        # We use input validation to ensure that usernames do not start with a
        # digit nor whitespace. Thus, if we are given an integer, it must be
        # a user ID, and a username otherwise.
        auth_user = req.context['user']
        try:
            try:
                requested_user = UserModel[int(username_or_id)]
            except ValueError:
                requested_user = UserModel.get(UserModel.username == username_or_id)
        except DoesNotExist:
            raise falcon.HTTPNotFound(
                description="The requested user does not exist."
            )

        resp.media = {
            "href": req.uri,
            "items": [requested_user.as_dict(req)]
        }
