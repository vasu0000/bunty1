from bottle import route, Bottle, request, response
from random import SystemRandom
from baseconv import BaseConverter
import sys
import re
from peewee import IntegrityError
import os
import json
from datetime import datetime, timedelta

import settings
from database import db, Dump

GOOD_CHARS = 'abcdefghkmnpqrstwxyz'
GOOD_DIGITS = '23456789'
CRYPTO_CHARS = GOOD_CHARS + GOOD_CHARS.upper() + GOOD_DIGITS
NUM_SYSTEM_CONVERTOR = BaseConverter(CRYPTO_CHARS)
APP = Bottle()
TIMEOUT_MAP = {
    's5': timedelta(seconds=5),
    'm10': timedelta(minutes=10),
    'h1': timedelta(hours=1),
    'd1': timedelta(days=1),
    'd7': timedelta(days=7),
    'd30': timedelta(days=30),
}


def create_dump(data, expires):
    gen = SystemRandom() 
    for x in range(10):
        new_id = gen.randint(1, sys.maxsize)
        try:
            with db.atomic():
                Dump.create(id=new_id, data=data, expires=expires)
        except IntegrityError:
            pass
        else:
            return new_id
    raise Exception('Could not generate unique ID for new dump')


@APP.route('/')
def page_home():
    return open(os.path.join(settings.BASE_DIR, 'templates/app.html')).read()


@APP.route('/api/dump', ['POST'])
def api_dump_post():
    isbot = request.forms.getunicode('iambot')
    if isbot:
        response.status = 403
        return 'Access denied'

    timeout = request.forms.getunicode('timeout')
    if timeout:
        if timeout not in TIMEOUT_MAP:
            response.status = 403
            return 'Timeout option is invalid'
        timeout = TIMEOUT_MAP[timeout]
    else:
        timeout = None

    data = request.forms.getunicode('data')
    if not data:
        response.status = 403
        return 'Data is empty'

    if timeout:
        expires = datetime.utcnow() + timeout
    else:
        expires = None
    dump_id = create_dump(data, expires)
    short_id = NUM_SYSTEM_CONVERTOR.encode(dump_id)
    return json.dumps({'dump_id': short_id})


@APP.route('/api/dump', ['GET'])
def api_dump_get():
    short_id = request.query.dump_id
    if re.compile('^[%s]+$' % CRYPTO_CHARS).match(short_id):
        dump_id = int(NUM_SYSTEM_CONVERTOR.decode(short_id))
        if dump_id <= sys.maxsize:
            try:
                dump = Dump.get(Dump.id == dump_id)
            except Dump.DoesNotExist:
                pass
            else:
                now = datetime.utcnow()
                if dump.expires and now > dump.expires:
                    with db.atomic():
                        dump.delete_instance()
                else:
                    if dump.expires:
                        expires_sec = (dump.expires - now).total_seconds()
                    else:
                        expires_sec = None
                    return json.dumps({
                        'dump': {
                            'data': dump.data,
                            'expires_sec': expires_sec,
                        }
                    })
    return json.dumps({
        'error': 'Invalid dump ID'
    })


@APP.route('/<short_id:re:[a-zA-Z0-9]{1,20}>')
def compatibility_redirect(short_id):
    response.headers['location'] = '/#%s' % short_id
    response.status = 302
    return response


if __name__ == '__main__':
    APP.run(host='localhost', port=9000, debug=True, reloader=True)
