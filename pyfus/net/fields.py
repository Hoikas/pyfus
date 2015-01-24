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
import struct
from uuid import UUID

@asyncio.coroutine
def _read_blob(fd, size):
    data = yield from fd.read(size)
    if len(data) != size:
        raise ConnectionResetError()
    return data

def _write_blob(fd, size, data):
    fd.write(data)

blob = (_read_blob, _write_blob)

@asyncio.coroutine
def _read_buffer(fd, size, maxsize):
    bufsz = yield from _read_integer(fd, size)
    if bufsz > maxsize:
        # somehow signal that the client needs to be booted
        pass
    data = yield from fd.read(bufsz)
    return data

def _write_buffer(fd, size, value):
    _write_integer(fd, size, len(value))
    fd.write(value)

# buffer size hints to prevent clients from sending us a load of crap
# tiny = 1KB; medium = 1MB; big = 10MB
tiny_buffer = (lambda fd, size: _read_buffer(fd, size, 1024), _write_buffer)
medium_buffer = (lambda fd, size: _read_buffer(fd, size, 1024 * 1024), _write_buffer)
big_buffer = (lambda fd, size: _read_buffer(fd, size, 10 * 1024 * 1024), _write_buffer)

@asyncio.coroutine
def _read_integer(fd, size):
    if size == 1:
        p = "<B"
    elif size == 2:
        p = "<H"
    elif size == 4:
        p = "<I"
    else:
        raise RuntimeError("Invalid integer field size: {}".format(size))

    data = yield from fd.read(size)
    if len(data) == size:
        return struct.unpack(p, data)[0]
    else:
        raise ConnectionResetError()

def _write_integer(fd, size, value):
    if size == 1:
        p = "<B"
    elif size == 2:
        p = "<H"
    elif size == 4:
        p = "<I"
    else:
        raise RuntimeError("Invalid integer field size: {}".format(size))
    fd.write(struct.pack(p, value))

integer = (_read_integer, _write_integer)

@asyncio.coroutine
def _read_string(fd, size):
    actualSize = size * 2
    buf = yield from fd.read(actualSize)
    if len(buf) != actualSize:
        raise ConnectionResetError()
    decoded = buf.decode("utf-16-le", errors="replace")
    return decoded.rstrip('\0')

def _write_string(fd, size, value):
    bSize = (size - 1) * 2
    buf = value.encode("utf-16-le", errors="replace")

    # Make sure the UTF-16 buffer is at least the blob size
    # Further, only send out blobsize-1 characters. Manually send null terminator
    buf = buf.ljust(bSize, b'\0')
    fd.write(buf)
    fd.write(struct.pack("H", 0))

string = (_read_string, _write_string)

@asyncio.coroutine
def _read_uuid(fd, size):
    assert size == 1
    data = yield from fd.read(16)
    if len(data) != 16:
        raise ConnectionResetError()
    return UUID(bytes_le=data)

def _write_uuid(fd, size, value):
    assert size == 1
    fd.write(value.bytes_le)

uuid = (_read_uuid, _write_uuid)
