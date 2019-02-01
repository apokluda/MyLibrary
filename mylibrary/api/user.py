import falcon
from falcon.media.validators import jsonschema

from peewee import *

from mylibrary.model.user import UserModel, DoesNotExist

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

class AllowedUsers(object):
    def __init__(self, users):
        self._users = users

    def __call__(self, req, resp, resource, params):
        user = req.context['user']
        if user['username'] not in self._users:
            raise falcon.HTTPUnauthorized(
                "Operation Not Permitted",
                "You do not have the permissions necessary to perform the requested operation."
            )


class Users(object):
    # Disable authentication on the POST method to allow anyone to create a
    # new user account. (Alternatively, we could require that the admin user
    # create all new user accounts)
    auth = {
        "exempt_methods": ["POST"]
    }

    @falcon.before(AllowedUsers(['admin']))
    def on_get(self, req, resp):
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
            if (username_or_id.isdigit()):
                print("Getting user by id")
                user = UserModel[username_or_id]
            else:
                print("Getting user by username")
                user = UserModel.get(UserModel.username == username_or_id)
            print("Found user " + user.username)
        except DoesNotExist:
            raise falcon.HTTPNotFound(
                title="User Not Found",
                description="The requested user could not be found.",
                # 404 status codes are cacheable by default; but new users can be
                # created at any time
                headers={"Cache-Control": "no-cache"}
            )
