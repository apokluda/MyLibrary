from peewee import *
import mylibrary

class BaseModel(Model):
    class Meta:
        database = mylibrary.db
