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
import sys

import crypto
import net
import settings

from . import filestructs as _msg

class FileSession(net.NetServerSession):
    # Yes, the FileSrv is a special case :(
    _msg_header = (
        (net.fields.integer, "msg_size", 4),
        (net.fields.integer, "msg_id", 4),
    )

    def __init__(self, client, parent):
        super(FileSession, self).__init__(client, parent)
        self.incoming_lookup = {
            10: (_msg.build_request, self.send_buildid)
        }
        self.outgoing_lookup = {
            _msg.build_reply: 10,
        }

    @asyncio.coroutine
    def send_buildid(self, req):
        reply = net.NetMessage(_msg.build_reply,
                               trans_id=req.trans_id,
                               result=0,
                               build_id=settings.product.build_id)
        yield from self.send_netstruct(reply)

class FileSrv(net.ServerBase):
    _conn_type = net.ServerID.file

    @asyncio.coroutine
    def accept_client(self, client):
        header = yield from net.read_netstruct(client.reader, _msg.connection_header)
        print(str(header))

        session = FileSession(client, self)
        self.clients.append(session)
        yield from session.dispatch_netstructs()


# Register thyself
net.register_server(FileSrv)
