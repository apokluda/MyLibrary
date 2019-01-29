import datetime

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
    def on_get(self, req, resp):
        resp.media = {'users':'I\'m working on it'}

    @jsonschema.validate(create_user_schema)
    def on_post(self, req, resp):
        doc = req.media
        user = UserModel(
            username=doc.get('username'),
            password=doc.get('password'),
            join_date=datetime.datetime.now()
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
