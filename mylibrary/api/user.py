import falcon
from falcon.media.validators import jsonschema

from peewee import *

from mylibrary.model import UserModel

create_user_schema = {
    "type": "object",
    "properties": {
        "username": {
            "description": "Desired username",
            "type": "string",
            "minLength": 1,
            "pattern": "^[^0-9]"
        },
        "password": {
            "description": "Your chosen password",
            "type": "string",
            "minLength": 6,
        }
    },
    "required": ["username", "password"]
}

class UserAPI(object):
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

        body = {
            "href": req.forwarded_uri,
            "items": []
        }

        for user in UserModel.select():
            print("appending user " + user.username)
            body['items'].append({"username" : user.username,
            "join_date": str(user.join_date),
            "href": req.forwarded_uri + "/" + str(user.id)})

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
            resp.location = '/user/{}'.format(doc['username'])
        except IntegrityError as e:
            raise falcon.HTTPBadRequest(
                "Username Unavailable",
                "The requsted username is already in use. Please try again.\n\nDetails: {}".format(e)
            )
