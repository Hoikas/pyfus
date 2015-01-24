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

import net
from . import rand, bignum, rc4

_c2s_connect = 0
_s2c_encrypt = 1

fields = net.fields
_connect_struct = (
    (fields.integer, "msg_id", 1),
    (fields.integer, "msg_size", 1),
    (fields.blob, "y_data", 64),
)

_encrypt_struct = (
    (fields.integer, "msg_id", 1),
    (fields.integer, "msg_size", 1),
    (fields.blob, "server_seed", 7),
)

class _RC4:
    def __init__(self, base, key):
        self._key = rc4.initialize(key)

        # Now we map the base to us
        for i in dir(base):
            if not hasattr(self, i):
                setattr(self, i, getattr(base, i))
        self._base = base

    @asyncio.coroutine
    def read(self, size):
        data = yield from self._base.read(size)
        return rc4.transform(self._key, data)

    def write(self, data):
        sendbuf = rc4.transform(self._key, data)
        self._base.write(sendbuf)


@asyncio.coroutine
def establish_encryption_c2s(client, gValue, nKey, xKey):
    b = rand.random_int(64)
    cliSeed = pow(xKey, b, nKey).to_bytes(64, byteorder="little")
    srvSeed = pow(gValue, b, nKey).to_bytes(64, byteorder="little")

    # Send our junk to the server
    ncc = net.NetMessage(_connect_struct,
                         msg_id=_c2s_connect,
                         msg_size=66,
                         y_data=srvSeed)
    net.write_netstruct(client.writer, ncc)
    yield from client.writer.drain()

    # Now, we get the seed from the server and make the key...
    nce = yield from net.read_netstruct(client.reader, _encrypt_struct)
    assert nce.msg_id == _s2c_encrypt
    assert nce.msg_size == 9

    key = bytearray(7)
    cliLen = len(cliSeed)
    for i in range(7):
        if i >= cliLen:
            key[i] = nce.server_seed[i]
        else:
            key[i] = cliSeed[i] ^ nce.server_seed[i]
    key = bytes(key)

    client.reader = _RC4(client.reader, key)
    client.writer = _RC4(client.writer, key)


@asyncio.coroutine
def establish_encryption_s2c(client, kKey, nKey):
    # We have some silly Cyanic stuff going on here... So, I'm going to use private methods.
    # Sue me!!!111eleventyeleven
    msgId = yield from fields._read_integer(client.reader, 1)
    msgSize = yield from fields._read_integer(client.reader, 1)

    # Cyan sends the TOTAL message size.
    msgSize -= 2

    # Sanity...
    assert msgId == _c2s_connect
    assert msgSize <= 64 or msgSize == 0

    # Okay, so, now here's our cleverness. If the message is empty, this is a decrypted connection.
    if msgSize:
        y_data = int.from_bytes((yield from client.reader.read(msgSize)), byteorder="little")
        cliSeed = pow(y_data, kKey, nKey).to_bytes(64, byteorder="little")
        srvSeed = rand.random_bytes(7)

        key = bytearray(7)
        cliLen = len(cliSeed)
        for i in range(7):
            if i >= cliLen:
                key[i] = srvSeed[i]
            else:
                key[i] = cliSeed[i] ^ srvSeed[i]
        key = bytes(key)

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
