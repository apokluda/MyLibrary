from peewee import *

import mylibrary
from .base import BaseModel

class UserModel(BaseModel):
    class Meta:
        table_name = "user"

    username = CharField(unique=True)
    password = CharField()
    join_date = DateTimeField()
