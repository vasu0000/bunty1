#!/usr/bin/env python
import logging
from peewee import IntegrityError
import re

from settings import DB_CONNECTION_URL
from database import db, Dump, Config


def get_migration_id(db):
    if 'config' not in db.get_tables():
        return 0
    return int(Config.get(Config.id == 'migration_id').value)


def set_migration_id(db, mid):
    try:
        with db.atomic():
            Config.create(id='migration_id', value=mid)
    except IntegrityError:
        with db.atomic():
            (Config.update(value=mid)
                   .where(Config.id == 'migration_id')
                   .execute())


def step1(db):
    db.create_tables([Config, Dump])


def step2(db):
    # Struggle with absense of DROP COLUMN in sqlite
    db.execute_sql('''
        CREATE TABLE dump_tmp AS
        SELECT id, data FROM dump
    ''')
    db.execute_sql('DROP TABLE dump')
    db.execute_sql('ALTER TABLE dump_tmp RENAME TO dump');


def get_max_migration_id():
    rex_mig = re.compile('^step(\d+)$')
    mids = []
    for name in globals().keys():
        match = rex_mig.match(name)
        if match:
            mids.append(int(match.group(1)))
    return max(mids)


def main():
    logging.info('Start migration')
    for mid in range(get_migration_id(db) + 1, get_max_migration_id() + 1):
        logging.info('Running migration#%d' % mid)
        globals()['step%d' % mid](db)
        set_migration_id(db, mid)
    logging.info('Done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
