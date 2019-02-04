import falcon
from falcon.media.validators import jsonschema

from peewee import *

from mylibrary.model.user import UserModel, DoesNotExist

from mylibrary.routes import routes
import mylibrary.schemas as schemas

class Users(object):
    # Disable authentication on the POST method to allow anyone to create a
    # new user account. (Alternatively, we could require that the admin user
    # create all new user accounts)
    auth = {
        "exempt_methods": ["POST"]
    }

    def on_get(self, req, resp):
        # It would make more sense to use forwarded_uri here, since this is
        # the original URI sent by the client for proxied requests, however
        # it does not included the original port. Perhaps this is a bug in
        # falcon?
        resp.media = {
            "href": req.uri,
            "items": [user.as_dict(req) for user in UserModel.select()]
        }

    @jsonschema.validate(schemas.create_user)
    def on_post(self, req, resp):
        doc = req.media
        user = UserModel(
            username=doc.get('username'),
            password=doc.get('password'),
        )
        try:
            user.save()
            resp.status = falcon.HTTP_CREATED
            resp.location = routes['user'].format(username_or_id=doc['username'])
        except IntegrityError as e:
            raise falcon.HTTPBadRequest(
                "Username Unavailable",
                "The requsted username is already in use. Please try again.\n\nDetails: {}".format(e)
            )

class User(object):
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
            "items": [requested_user.as_dict(req, True)]
        }
