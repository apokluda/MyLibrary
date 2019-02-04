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

    @jsonschema.validate(schemas.create_book)
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
    def __book_not_found(self):
        return falcon.HTTPNotFound(
            description="The requested book does not exist."
        )

    def on_get(self, req, resp, id):
        # We use input validation to ensure that usernames do not start with a
        # digit nor whitespace. Thus, if we are given an integer, it must be
        # a user ID, and a username otherwise.
        auth_user = req.context['user']
        try:
            try:
                requested_book = BookModel[int(id)]
            except ValueError:
                raise self.__book_not_found()
        except DoesNotExist:
            raise self.__book_not_found()

        resp.media = {
            "href": req.uri,
            "items": [requested_book.as_dict(req)]
        }
