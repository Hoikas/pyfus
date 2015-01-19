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

import crypto
import net
import settings

from . import gatestructs as _msg

class GateKeeperSession(net.NetStructDispatcher):
    def __init__(self, client):
        super(GateKeeperSession, self).__init__(client)
        self.lookup = {
            0: (_msg.ping_pong, self.ping_pong),
            1: (_msg.authsrv_request, self.authsrv_request),
        }

    @asyncio.coroutine
    def authsrv_request(self, req):
        print(str(req))

    @asyncio.coroutine
    def ping_pong(self, ping):
        print(str(ping))


class GateKeeperSrv(net.ServerBase):
    _conn_type = 22

    def __init__(self):
        self._clients = []

    @asyncio.coroutine
    def accept_client(self, client):
        # First, receive the gate connection header.
        # This is some Cyan copypasta garbage... :(
        header = yield from net.read_netstruct(client.reader, _msg.connection_header)
        print(str(header))

        # Now, establish the encryption...
        yield from crypto.establish_encryption_s2c(client, self._k, self._n)

        # Blarg
        session = GateKeeperSession(client)
        self._clients.append(session)
        yield from session.dispatch_netstructs(session.lookup)

    def start(self, loop):
        self._k = self.decode_key(settings.gatekeeper.k_key)
        self._n = self.decode_key(settings.gatekeeper.n_key)


# Register the GateKeeperSrv
net.register_server(GateKeeperSrv)
