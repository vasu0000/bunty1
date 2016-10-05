import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DB_CONNECTION_URL = 'sqlite:///%s' % (os.path.join(BASE_DIR,
                                                   'var/sbin.sqlite'))
try:
    from settings_local import *
except ImportError:
    pass
