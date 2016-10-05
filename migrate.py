#!/usr/bin/env python
import logging
from peewee import IntegrityError

from web import DB

MAX_MIGRATION_ID = 1


def get_migration_id(db):
    if 'config' not in db.get_tables():
        return 0
    res = db.execute_sql('''
        SELECT value FROM config
        WHERE id = 'migration_id'
    ''')
    return int(res.fetchone()[0])


def set_migration_id(db, mid):
    try:
        with db.atomic():
            db.execute_sql('''
                INSERT INTO config (id, value)
                VALUES ('migration_id', '%d')
            ''' % mid)
    except IntegrityError:
        with db.atomic():
            db.execute_sql('''
                UPDATE config SET value = '%d'
                WHERE id = 'migration_id'
            ''' % mid)


def step1(db):
    with db.atomic():
        db.execute_sql('''
            CREATE TABLE config (
                id TEXT(20) PRIMARY KEY,
                value TEXT
            ) WITHOUT ROWID
        ''')
        db.execute_sql('''
            CREATE TABLE dump (
                id INTEGER(8) PRIMARY KEY,
                data BLOB,
                has_password INTEGER(1)
            ) WITHOUT ROWID
        ''')


#def step2(db):
#    pass


def main():
    logging.info('Start migration')
    for mid in range(get_migration_id(DB) + 1, MAX_MIGRATION_ID + 1):
        logging.info('Running migration#%d' % mid)
        globals()['step%d' % mid](DB)
        set_migration_id(DB, mid)
    logging.info('Done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
