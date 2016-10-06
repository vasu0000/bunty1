"""
This is example of decrypting data encrypted with http://bin.so service
Change url and password variables to test your own bin.so dump
This is python3 script
"""
from base64 import b64decode
from urllib.request import urlopen
import json
import re

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def main():
    # Configuration
    url = 'http://bin.so/cTzgArbRP9g9'
    password = 'pass'

    data = urlopen(url).read().decode('utf-8')
    data = re.search('<pre[^>]+>(.+?)</pre>', data).group(1).strip()
    data = b64decode(data).decode('utf-8')
    opts = json.loads(data)
    if opts['mode'] != 'gcm':
        raise Exception('This script works only with data encrypted in AES GCM mode')

    # Convert base64-encoded values into bytes
    for key in ('ct', 'iv', 'salt', 'adata'):
        opts[key] = b64decode(opts[key])
    # Build the key using salt and iteration number from opts
    backend = default_backend()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=(128//8),
        salt=opts['salt'],
        iterations=opts['iter'],
        backend=backend
    )
    key = kdf.derive(password.encode('utf-8'))

    # Split cipher text into data and tag, length of tag is 16 bytes (opts['ts'])
    data = opts['ct'][:-16]
    tag = opts['ct'][-16:]

    # Use AES in GCM mode 
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(opts['iv'], tag),
        backend=backend,
    )
    dec = cipher.decryptor()
    dec.authenticate_additional_data(opts['adata'])
    data = (dec.update(data) + dec.finalize()).decode('utf-8')
    print(data)


if __name__ == '__main__':
    main()
