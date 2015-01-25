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
import codecs
import io
import weakref

from . import fields
import settings

connection_header = (
    (fields.integer, "conn_type", 1),
    (fields.integer, "size", 2),
    (fields.integer, "build_id", 4),
    (fields.integer, "build_type", 4),
    (fields.integer, "branch_id", 4),
    (fields.uuid, "product", 1),
)

class NetMessage:
    def __init__(self, struct, **kwargs):
        self._struct = struct
        self.__dict__.update(kwargs)

    def __str__(self):
        detail = "NetMessage\n"
        for i in dir(self):
            if i.startswith("_"):
                continue
            detail += "    '{}': \"{}\"\n".format(i, getattr(self, i))
        return detail


@asyncio.coroutine
def read_netstruct(fd, struct):
    """Reads a message off the wire defined by the given struct"""

    msg = NetMessage(struct)
    for rw, name, size in struct:
        data = yield from rw[0](fd, size)
        setattr(msg, name, data)
    return msg

def write_netstruct(fd, msg):
    def _debug(msg, data):
        hex = codecs.encode(data, "hex")
        print("{}\n{}\n".format(msg._struct, hex))

    # Unfortunately, the client arseplodes if we send the buffer bit-by-bit in some cases...
    # So, we're going to have to buffer it locally.
    bio = io.BytesIO()
    for rw, name, size in msg._struct:
        data = getattr(msg, name)
        rw[1](bio, size, data)

    data = bio.getvalue()
    #_debug(msg, data)
    fd.write(data)

class NetStructDispatcher:
    """Dispatches NetStructs read off the wire to callables"""

    def __init__(self, idSize=2, hasMsgSize=False):
        self._id_size = idSize
        self._has_msg_size = hasMsgSize
        self.reader = None
        self.writer = None

    @asyncio.coroutine
    def dispatch_netstructs(self):
        header_struct = []
        if self._has_msg_size:
            header_struct.append((fields.integer, "msg_size", self._id_size))
        header_struct.append((fields.integer, "msg_id", self._id_size))

        while True:
            try:
                header = yield from read_netstruct(self.reader, header_struct)
            except (asyncio.CancelledError, ConnectionError):
                self.connection_reset()
                break

            try:
                msg_struct, handler = self.incoming_lookup[header.msg_id]
            except LookupError:
                # TODO: log error
                self.connection_reset()
                return

            if msg_struct is None:
                asyncio.async(handler())
            else:
                try:
                    actual_netmsg = yield from read_netstruct(self.reader, msg_struct)
                except (asyncio.CancelledError, ConnectionError):
                    self.connection_reset()
                    break
                else:
                    asyncio.async(handler(actual_netmsg))

    def connection_reset(self):
        if self.writer is not None:
            # This closes the transport
            self.writer.close()

    @asyncio.coroutine
    def send_netstruct(self, netmsg):
        netstruct = netmsg._struct
        wantSize = self._has_msg_size
        size = self._id_size
        if wantSize:
            writer = io.BytesIO()
        else:
            writer = self.writer

        msg_id = self.outgoing_lookup[netstruct]
        fields._write_integer(writer, size, msg_id)
        write_netstruct(writer, netmsg)

        if wantSize:
            buffer = writer.getbuffer()
            # Remember, eap size is the entire size (msgSize + msgId + payload)
            fields._write_integer(self.writer, size, len(buffer) + size)
            self.writer.write(buffer)

        try:
            yield from self.writer.drain()
        except (asyncio.CancelledError, ConnectionError):
            self.connection_reset()


class NetClient(NetStructDispatcher):
    @asyncio.coroutine
    def _finalize_connection(self):
        pass

    @asyncio.coroutine
    def start(self):
        self.reader, self.writer = yield from asyncio.open_connection(settings.lobby.host, settings.lobby.port)
        hdr = NetMessage(connection_header,
                         conn_type=self._conn_type,
                         size=31,
                         build_id=settings.product.build_id,
                         build_type=50,
                         branch_id=1,
                         product=settings.product.uuid)
        write_netstruct(self.writer, hdr)
        try:
            yield from self.writer.drain()
            yield from self._finalize_connection()
            yield from self.dispatch_netstructs()
        except (asyncio.CancelledError, ConnectionError):
            self.connection_reset()


class NetServerSession(NetStructDispatcher):
    def __init__(self, client, parent, idSize=2, hasMsgSize=False):
        super(NetServerSession, self).__init__(idSize, hasMsgSize)
        self.reader = client.reader
        self.writer = client.writer
        self._parent = weakref.ref(parent)

    def connection_reset(self):
        super(NetServerSession, self).connection_reset()
        self._parent().clients.remove(self)
