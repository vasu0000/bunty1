from bottle import route, Bottle, request, response, static_file
from jinja2 import Environment, FileSystemLoader
from random import SystemRandom
from baseconv import BaseConverter
import sys
import re
import logging
from peewee import IntegrityError
import os

import settings
from database import db, Dump

GOOD_CHARS = 'abcdefghkmnpqrstwxyz'
GOOD_DIGITS = '23456789'
CRYPTO_CHARS = GOOD_CHARS + GOOD_CHARS.upper() + GOOD_DIGITS
ENV = Environment(loader=FileSystemLoader([
    os.path.join(settings.BASE_DIR, 'templates_local'),
    os.path.join(settings.BASE_DIR, 'templates'),
]))
CONV = BaseConverter(CRYPTO_CHARS)
app = Bottle()


def render(tpl_name, **kwargs):
    tpl = ENV.get_template(tpl_name)
    return tpl.render(**kwargs)


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


@app.route('/')
def home_page():
    return render('add.html')


@app.route('/dump/add', ['GET', 'POST'])
def add_page():
    if request.method == 'GET':
        return render('add.html')
    else:
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
            #import pdb; pdb.set_trace()
            short_id = CONV.encode(dump_id)
            response.headers['location'] = '/%s' % short_id
            response.status = 302
            return response


@app.route('/<short_id:re:[a-zA-Z0-9]{1,20}>')
def dump_page(short_id):
    if re.compile('^[%s]+$' % CRYPTO_CHARS).match(short_id):
        dump_id = int(CONV.decode(short_id))
        if dump_id <= sys.maxsize:
            try:
                dump = Dump.get(Dump.id == dump_id)
            except Dump.DoesNotExist:
                pass
            else:
                return render('dump.html', data=dump.data,
                              has_password=dump.has_password)
    response.status = 404
    return '<h3 style="color: red">Invalid dump ID</h3>'


@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')


@app.route('/help/faq')
def faq_page():
    return render('faq.html')


if __name__ == '__main__':
    app.run(host='localhost', port=9000, debug=True, reloader=True)
