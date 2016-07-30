#!/usr/bin/env python
from peewee import *

db = SqliteDatabase('asr.db')

class ASRClass(Model):
    name = CharField(index=True)
    date = DateField(index=True)
    present = CharField()
    available_nb = IntegerField()
    total_nb = IntegerField()

    class Meta:
        database = db


if __name__ == '__main__':
    db.connect()
    db.create_tables([ASRClass])
