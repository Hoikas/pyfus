#    fus - fast uru server
#    Copyright (C) 2014  Adam 'Hoikas' Johnson <AdamJohnso AT gmail DOT com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import os

from net import fields
from . import rand, bignum

_c2s_connect = 0
_s2c_encrypt = 1

class _RC4:
    def __init__(self, base, key):
        x = 0
        self._state = list(range(256))
        for i in range(256):
            x = (key[i % len(key)] + self._state[i] + x) & 0xFF
            self._state[i], self._state[x] = self._state[x], self._state[i]

        # State stuff
        self._x = 0
        self._y = 0

        # Now we map the base to us
        for i in dir(base):
            if not hasattr(self, i):
                setattr(self, i, getattr(base, i))
        self._base = base

    def _rc4(self, data):
        for i in range(len(data)):
            self._x = (self._x + 1) & 0xFF
            self._y = (self._state[self._x] + self._y) & 0xFF
            self._state[self._x], self._state[self._y] = self._state[self._y], self._state[self._x]
            data[i] = (data[i] ^ self._state[(self._state[self._x] + self._state[self._y]) & 0xFF])

    @asyncio.coroutine
    def read(self, size):
        data = yield from self._base.read(size)
        self._rc4(data)
        return data

    def write(self, data):
        self._rc4(data)
        self._base.write(data)


@asyncio.coroutine
def establish_encryption_s2c(client, kKey, nKey):
    print("moogalooga!")
    # We have some silly Cyanic stuff going on here... So, I'm going to use private methods.
    # Sue me!!!111eleventyeleven
    msgId = yield from fields._read_integer(client.reader, 1)
    msgSize = yield from fields._read_integer(client.reader, 1)

    # Cyan sends the TOTAL message size.
    msgSize -= 2

    # Sanity...
    assert msgId == _c2s_connect
    assert msgSize <= 64

    # Okay, so, now here's our cleverness. If the message is empty, this is a decrypted connection.
    if msgSize:
        y_data = int.from_bytes((yield from client.reader.read(msgSize)), byteorder="big")
        cliSeed = pow(y_data, kKey, nKey).to_bytes(64, byteorder="little")
        srvSeed = rand.random_bytes(7)

        key = bytearray(7)
        for i in range(len(key)):
            if i >= len(cliSeed):
                key[i] = srvSeed[i]
            else:
                key[i] = cliSeed[i] ^ srvSeed[i]

        # NetCliEncrypt
        fields._write_integer(client.writer, 1, _s2c_encrypt)
        fields._write_integer(client.writer, 1, 9)
        client.writer.write(srvSeed)
        yield from client.writer.drain()

        # Now set up our encrypted reader/writer
        client.reader = _RC4(client.reader, key)
        client.writer = _RC4(client.writer, key)
    else:
        # NetCliEncrypt... but not really
        fields._write_integer(client.writer, 1, _s2c_encrypt)
        fields._write_integer(client.writer, 1, 2)
        yield from client.writer.drain()

def generate_keys(gValue):
    """Generates public, private, and shared keys for an Uru server"""
    k = bignum.generate_prime(512)
    n = bignum.generate_prime(512)
    x = pow(gValue, k, n)
    return (k.to_bytes(64, byteorder="big"), n.to_bytes(64, byteorder="big"), x.to_bytes(64, byteorder="big"))
