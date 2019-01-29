from peewee import *

import mylibrary

class UserModel(Model):
    username = CharField()
    real_name = CharField()

    class Meta:
        table_name = "User"
        database = mylibrary.db
