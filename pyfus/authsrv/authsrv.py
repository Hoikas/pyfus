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

from . import authstructs as _msg

class AuthSession(net.NetServerSession):
    def __init__(self, client, parent):
        super(AuthSession, self).__init__(client, parent)
        self.incoming_lookup = {
            0: (_msg.ping_pong, self.ping_pong),
        }

    @asyncio.coroutine
    def ping_pong(self, ping):
        print(str(ping))


class AuthSrv(net.ServerBase):
    _conn_type = net.ServerID.auth
    _k = net.decode_key(settings.auth.k_key)
    _n = net.decode_key(settings.auth.n_key)

    @asyncio.coroutine
    def accept_client(self, client):
        # First, receive the auth connection header.
        header = yield from net.read_netstruct(client.reader, _msg.connection_header)

        # Now, establish the encryption...
        yield from crypto.establish_encryption_s2c(client, self._k, self._n)

        # Okay, now we have our dude
        session = AuthSession(client, self)
        self.clients.append(session)
        yield from session.dispatch_netstructs()


# Register the GateKeeperSrv
net.register_server(AuthSrv)
