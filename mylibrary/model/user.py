import datetime

from peewee import *

import mylibrary
from .base import BaseModel

# NOTE: This is just an exercise. In a real implementation we would
# never store a plain text password! Peewee has a nice example demonstrating
# password hashing: http://docs.peewee-orm.com/en/latest/peewee/hacks.html#writing-custom-functions-with-sqlite

class UserModel(BaseModel):
    class Meta:
        table_name = "user"

    username = CharField(unique=True)
    password = CharField()
    join_date = DateTimeField(default=datetime.datetime.utcnow)
