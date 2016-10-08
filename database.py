import settings
from playhouse import db_url
from peewee import *

db = db_url.connect(settings.DB_CONNECTION_URL)


class Config(Model):
    id = FixedCharField(primary_key=True, max_length=20)
    value = TextField()

    class Meta:
        database = db

class Dump(Model):
    id = BigIntegerField(primary_key=True)
    data = TextField()

    class Meta:
        database = db
