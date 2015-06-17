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
import importlib
import sys

from constants import *
import crypto
import net
import settings

from .dbfus import FusDatabase
from . import dbstructs as _msg
from .dbpool import DbPool

class DbSrvSession(net.NetServerSession):
    def __init__(self, client, parent):
        super(DbSrvSession, self).__init__(client, parent)
        self.incoming_lookup = {
            0: (_msg.ping_pong, self.ping_pong),
        }
        self.outgoing_lookup = {
        }

    @asyncio.coroutine
    def ping_pong(self, ping):
        pass


class DbSrv(net.ServerBase):
    _conn_type = NetProtocol.db
    _k = net.decode_key(settings.db.k_key)
    _n = net.decode_key(settings.db.n_key)

    @asyncio.coroutine
    def accept_client(self, client):
        # Establish the encryption...
        yield from crypto.establish_encryption_s2c(client, self._k, self._n)

        # Okay, now we have our dude
        session = DbSrvSession(client, self)
        self.clients.append(session)
        yield from session.dispatch_netstructs()

    def start(self, loop):
        super().start(loop)

        # Make sure our database of choice is initialized before we start serving any clients
        db = FusDatabase()
        loop.run_until_complete(db.connect_ini())
        db.initialize()


# Register the DbSrv
net.register_server(DbSrv)
