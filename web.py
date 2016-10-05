from bottle import route, Bottle, request, response, static_file
from jinja2 import Environment, FileSystemLoader
from pymongo.errors import DuplicateKeyError
from random import SystemRandom
import sqlite3
from baseconv import BaseConverter
import sys
import re

GOOD_CHARS = 'abcdefghkmnpqrstwxyz'
GOOD_DIGITS = '23456789'
CRYPTO_CHARS = GOOD_CHARS + GOOD_CHARS.upper() + GOOD_DIGITS
DB = sqlite3.connect('var/sbin.sqlite')
ENV = Environment(loader=FileSystemLoader('templates'))
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
            DB.execute('''
                INSERT INTO dump (id, data, has_password)
                VALUES (?, ?, ?)
            ''', (new_id, data, 1 if has_password else 0))
            DB.commit()
        except sqlite3.IntegrityError:
            pass
        else:
            return new_id
    raise Exception('Could not generate unique ID for new dump')


@app.route('/')
def home_page():
    return render('home.html')


@app.route('/dump/add', ['GET', 'POST'])
def home_page():
    if request.method == 'GET':
        return render('home.html')
    else:
        data = request.forms.getunicode('data')
        has_password = request.forms.getunicode('has_password') == 'yes'
        if not data:
            return render('home.html', data_error='Data is empty')
        dump_id = create_dump(data, has_password)
        #import pdb; pdb.set_trace()
        short_id = CONV.encode(dump_id)
        response.headers['location'] = '/%s' % short_id
        response.status = 302
        return response


@app.route('/<short_id:re:[a-zA-Z0-9]{1,20}>')
def dump_page(short_id):
    if not re.compile('^[%s]+$' % CRYPTO_CHARS).match(short_id):
        response.status = 404
        return '<h3 style="color: red">Invalid dump ID</h3>'
    dump_id = CONV.decode(short_id)
    res = DB.execute('''
        SELECT data, has_password FROM dump
        WHERE id = ?
    ''', (dump_id,))
    row = res.fetchone()
    if row is None:
        response.status = 404
        return '<h3 style="color: red">Invalid dump ID</h3>'
    else:
        data, has_password = row
        return render('dump.html', data=data, has_password=has_password)
        #response.headers['content-type'] = 'text/plain'
        #return row[0]


@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')


if __name__ == '__main__':
    app.run(host='localhost', port=9000, debug=True, reloader=True)
