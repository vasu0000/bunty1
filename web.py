from random import SystemRandom
import sys
import re
import os
import time
import json
import six
from pprint import pprint

from bottle import route, Bottle, request, response
from baseconv import BaseConverter

VERSION = '0.0.2'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
app = Bottle()
TIMEOUT_MAP = {
    'm10': 60 * 10,
    'h1': 60 * 60,
    'd1': 24 * 60 * 60,
    'd7': 7 * 24 * 60 * 60,
    'd30': 30 * 24 * 60 * 60,
}


class NumSystemConvertor(object):
    crypto_chars = (
        'abcdefghkmnpqrstwxyz'
        'ABCDEFGHKMNPQRSTWXYZ'
        '23456789'
    )
    engine = BaseConverter(crypto_chars)

    @classmethod
    def encode(cls, dec_num):
        return cls.engine.encode(dec_num)

    @classmethod
    def decode(cls, val):
        return cls.engine.decode(val)


def prepare_location_dirs(path):
    dir_, fname = os.path.split(path)
    try:
        os.makedirs(dir_)
    except OSError:
        pass


def get_dump_location(dump_id, storage_dir='dumps'):
    assert isinstance(dump_id, int)
    dump_id = NumSystemConvertor.encode(dump_id)
    padded_id = pad_dump_id(dump_id) 
    return '%s/%s/%s/%s' % (
        storage_dir,
        padded_id[:2],
        padded_id[2:4],
        padded_id,
    )


def save_dump(obj, file_handler):
    assert set(obj.keys()) == set(['id', 'data', 'created', 'expires'])
    assert isinstance(obj['id'], int)
    assert isinstance(obj['data'], six.text_type)
    assert isinstance(obj['created'], int)
    assert obj['expires'] is None or isinstance(obj['expires'], int)
    json.dump(obj, file_handler)


def pad_dump_id(val):
    """Pad dump ID with leading zeros
    to make lenght of ID equal to 12"""
    return '0' * (12 - len(val)) + val


def create_dump(data, expires):
    import fcntl

    gen = SystemRandom() 
    for x in range(10):
        new_id = gen.randint(1, sys.maxsize)
        location = get_dump_location(new_id)
        prepare_location_dirs(location)
        fobj = open(location, 'a+')
        try:
            fcntl.lockf(fobj, fcntl.LOCK_EX)
            if fobj.read():
                raise OSError
        except OSError:
            pass
        else:
            save_dump({
                'id': new_id,
                'data': data,
                'created': int(time.time()),
                'expires': expires,
            }, fobj)
            print('New dump saved to %s' % location)
            return new_id
        finally:
            fobj.close()
    raise Exception('Could not generate unique ID for new dump')


@app.route('/')
def page_home():
    with open(os.path.join(BASE_DIR, 'templates/app.html')) as inp:
        return inp.read()


@app.route('/api/dump', ['POST'])
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
        expires = int(time.time()) + timeout
    else:
        expires = None
    dump_id = create_dump(data, expires)
    short_id = NumSystemConvertor.encode(dump_id)
    return json.dumps({'dump_id': short_id})


def load_dump(dump_id):
    with open(get_dump_location(dump_id)) as inp:
        return json.load(inp)
   

@app.route('/api/dump', ['GET'])
def api_dump_get():
    short_id = request.query.dump_id
    if re.compile('^[%s]+$' % NumSystemConvertor.crypto_chars).match(short_id):
        dump_id = int(NumSystemConvertor.decode(short_id))
        if dump_id <= sys.maxsize:
            try:
                dump = load_dump(dump_id)
            except IOError:
                pass
            else:
                now = time.time()
                if dump['expires'] and now > dump['expires']:
                    try:
                        os.unlink(get_dump_location(dump_id))
                    except OSError:
                        pass
                else:
                    if dump['expires']:
                        expires_sec = int(dump['expires'] - now)
                    else:
                        expires_sec = None
                    return json.dumps({
                        'dump': {
                            'data': dump['data'],
                            'expires_sec': expires_sec,
                        }
                    })
    return json.dumps({
        'error': 'Invalid dump ID'
    })


@app.route('/<short_id:re:[a-zA-Z0-9]{1,20}>')
def compatibility_redirect(short_id):
    response.headers['location'] = '/#%s' % short_id
    response.status = 302
    return response


if __name__ == '__main__':
    app.run(host='localhost', port=9000, debug=True)#, reloader=True)
