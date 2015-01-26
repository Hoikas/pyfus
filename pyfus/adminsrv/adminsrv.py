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

from . import adminstructs as _msg

class AdminSession(net.NetServerSession):
    def __init__(self, client, parent):
        super(AdminSession, self).__init__(client, parent)
        self.incoming_lookup = {
            0: (_msg.shutdown_request, self.shutdown_shard),
        }
        self.outgoing_lookup = {
            
        }

    @asyncio.coroutine
    def shutdown_shard(self, msg):
        self.log_info("shutdown requested: '{}'".format(msg.message))
        print(msg.message)

        # Schedule the shutdown to start soon. We don't want to deadlock!
        lobby = net.fetch_server(net.ServerID.lobby)
        asyncio.get_event_loop().call_later(2, lobby.shutdown())

class AdminSrv(net.ServerBase):
    _conn_type = net.ServerID.admin
    _k = net.decode_key(settings.admin.k_key)
    _n = net.decode_key(settings.admin.n_key)

    @asyncio.coroutine
    def accept_client(self, client):
        yield from crypto.establish_encryption_s2c(client, self._k, self._n)

        session = AdminSession(client, self)
        self.clients.append(session)
        yield from session.dispatch_netstructs()


# Register thyself
net.register_server(AdminSrv)
