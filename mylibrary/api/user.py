import falcon
from falcon.media.validators import jsonschema

from peewee import *

from mylibrary.model import UserModel

from mylibrary.routes import routes

create_user_schema = {
    "type": "object",
    "properties": {
        "username": {
            "description": "Desired username",
            "type": "string",
            "minLength": 1,
            "pattern": "^[^\\d\\s]"
        },
        "password": {
            "description": "Your chosen password",
            "type": "string",
            "minLength": 6,
        }
    },
    "required": ["username", "password"]
}

class Users(object):
    # Disable authentication on the POST method to allow anyone to create a
    # new user account. (Alternatively, we could require that the admin user
    # create all new user accounts)
    auth = {
        "exempt_methods": ["POST"]
    }

    def on_get(self, req, resp):
        user = req.context['user']
        if user['username'] != 'admin':
            raise falcon.HTTPUnauthorized(
                "Operation Not Permitted",
                "Only admin can list all users"
            )

        # It would make more sense to use forwarded_uri here, since this is
        # the original URI sent by the client for proxied requests, however
        # it does not included the original port. Perhaps this is a bug in
        # falcon?
        body = {
            "href": req.uri,
            "items": []
        }

        for user in UserModel.select():
            body['items'].append({"username" : user.username,
            "join_date": str(user.join_date),
            "href": req.prefix + routes['user'].format(username_or_id=str(user.id))})

        resp.media = body

    @jsonschema.validate(create_user_schema)
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
        try:
            print("You requsted id " + str(int(username_or_id)))
        except ValueError:
            print("You requested username " + username_or_id)
