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
import util

kablooey = (asyncio.CancelledError, ConnectionError, EOFError)

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
    """Writes a NetStruct to a given fd and returns the number of bytes written. If fd is None, then
       the buffered data is returned instead"""
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
    if fd is not None:
        #_debug(msg, data)
        fd.write(data)
        return len(data)
    else:
        return data

class NetStructDispatcher:
    """Dispatches NetStructs read off the wire to callables"""

    # This is the most common message header...
    _msg_header = (
        (fields.integer, "msg_id", 2),
    )

    def __init__(self, reader=None, writer=None, log=None):
        self._msg_header_size = sum(list(zip(*self._msg_header))[2])
        self.reader = reader
        self.writer = writer

        self._log = log
        self.log_debug = lambda msg: self._log.debug("[{}] {}".format(self.peername, msg))
        self.log_info = lambda msg: self._log.info("[{}] {}".format(self.peername, msg))
        self.log_warn = lambda msg: self._log.warn("[{}] {}".format(self.peername, msg))
        self.log_error = lambda msg: self._log.error("[{}] {}".format(self.peername, msg))

    @asyncio.coroutine
    def dispatch_netstructs(self):
        while True:
            try:
                header = yield from read_netstruct(self.reader, self._msg_header)
            except kablooey:
                self.connection_reset()
                break

            try:
                msg_struct, handler = self.incoming_lookup[header.msg_id]
            except LookupError:
                self.log_warn("invalid messageID {}".format(header.msg_id))
                self.connection_reset()
                return

            if msg_struct is None:
                asyncio.async(handler())
            else:
                try:
                    actual_netmsg = yield from read_netstruct(self.reader, msg_struct)
                except kablooey:
                    self.connection_reset()
                    break
                else:
                    asyncio.async(handler(actual_netmsg))

    def connection_reset(self):
        if self.writer is not None:
            # This closes the transport
            self.writer.close()

    @property
    def peername(self):
        return "{}/{}".format(*self.writer.get_extra_info("peername"))

    @asyncio.coroutine
    def send_netstruct(self, netmsg):
        msgBuf = write_netstruct(None, netmsg)
        msgId = self.outgoing_lookup[netmsg._struct]
        header = NetMessage(self._msg_header,
                            msg_id=msgId,
                            msg_size=self._msg_header_size+len(msgBuf))
        headerBuf = write_netstruct(None, header)

        sendBuf = headerBuf + msgBuf
        self.writer.write(sendBuf)
        try:
            yield from self.writer.drain()
        except kablooey:
            self.connection_reset()


class NetClient(NetStructDispatcher):
    def __init__(self):
        log = util.find_log(self.__class__.__name__)
        super(NetClient, self).__init__(log=log)

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
        except kablooey:
            self.connection_reset()


class NetServerSession(NetStructDispatcher):
    def __init__(self, client, parent):
        super(NetServerSession, self).__init__(client.reader, client.writer, parent._log)
        self._parent = weakref.ref(parent)

    def connection_reset(self):
        self.log_debug("connection reset")
        super(NetServerSession, self).connection_reset()
        self._parent().clients.remove(self)

    @asyncio.coroutine
    def dispatch_netstructs(self):
        self.log_debug("client connected")
        yield from super(NetServerSession, self).dispatch_netstructs()
