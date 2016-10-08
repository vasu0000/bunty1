from bottle import route, Bottle, request, response
from random import SystemRandom
from baseconv import BaseConverter
import sys
import re
from peewee import IntegrityError
import os
import json

import settings
from database import db, Dump

GOOD_CHARS = 'abcdefghkmnpqrstwxyz'
GOOD_DIGITS = '23456789'
CRYPTO_CHARS = GOOD_CHARS + GOOD_CHARS.upper() + GOOD_DIGITS
NUM_SYSTEM_CONVERTOR = BaseConverter(CRYPTO_CHARS)
APP = Bottle()


def create_dump(data, has_password):
    gen = SystemRandom() 
    for x in range(10):
        new_id = gen.randint(1, sys.maxsize)
        try:
            with db.atomic():
                Dump.create(id=new_id, data=data,
                            has_password=1 if has_password else 0)
        except IntegrityError:
            pass
        else:
            return new_id
    raise Exception('Could not generate unique ID for new dump')


@APP.route('/')
def page_home():
    return open(os.path.join(settings.BASE_DIR, 'templates/app.html'))


@APP.route('/api/dump', ['POST'])
def api_dump_post():
    isbot = request.forms.getunicode('iambot')
    if isbot:
        response.status = 403
        return 'Access denied'
    else:
        data = request.forms.getunicode('data')
        has_password = request.forms.getunicode('has_password') == 'yes'
        if not data:
            return render('add.html', data_error='Data is empty')
        dump_id = create_dump(data, has_password)
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
                return json.dumps({
                    'dump': {
                        'has_password': bool(dump.has_password),
                        'data': dump.data,
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
