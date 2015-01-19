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
from . import fields

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
    for io, name, size in struct:
        data = yield from io[0](fd, size)
        setattr(msg, name, data)
    return msg


class NetStructDispatcher:
    """Dispatches NetStructs read off the wire to callables"""

    def __init__(self, client):
        self.reader = client.reader
        self.writer = client.writer

    @asyncio.coroutine
    def dispatch_netstructs(self, lookup, idSize=2, hasMsgSize=False):
        header_struct = []
        if hasMsgSize:
            header_struct.append((fields.integer, "msg_size", idSize))
        header_struct.append((fields.integer, "msg_id", idSize))

        # FIXME: Better logic
        while True:
            header = yield from read_netstruct(self.reader, header_struct)
            print(str(header))
            msg_struct, handler = lookup[header.msg_id]
            actual_netmsg = yield from read_netstruct(self.reader, msg_struct)
            asyncio.async(handler(actual_netmsg))
