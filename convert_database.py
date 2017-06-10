#!/usr/bin/env python
from pprint import pprint
import json
import os
from datetime import datetime

from database import Dump
from web import get_dump_location, save_dump, prepare_location_dirs


def main():
    for dump in Dump.select():
        location = get_dump_location(dump.id)
        print('Saving dump[%d] to %s' % (dump.id, location))
        if dump.expires:
            expires = int(
                (dump.expires - datetime(1970, 1, 1)).total_seconds()
            )
        else:
            expires = None
        obj = {
            'id': dump.id,
            'data': dump.data,
            'created': int((datetime.utcnow() - dump.created).total_seconds()),
            'expires': expires,
        }
        prepare_location_dirs(location)
        with open(location, 'w') as out:
            save_dump(obj, out)


if __name__ == '__main__':
    main()
