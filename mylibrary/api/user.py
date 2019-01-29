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
        "real_name": {
            "description": "Your full name",
            "type": "string"
        }
    },
    "required": ["username"]
}

class UserAPI(object):
    def on_get(self, req, resp):
        resp.media = {'users':'I\'m working on it'}

    @jsonschema.validate(create_user_schema)
    def on_post(self, req, resp):
        doc = req.media
        user = UserModel(username=doc.get('username'),real_name=doc.get('real_name', ""))
        user.save()

        resp.status = falcon.HTTP_CREATED
        resp.location = '/user/{}'.format(doc['username'])
