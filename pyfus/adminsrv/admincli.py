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

from . import adminstructs as _msg

class AdminCli(net.NetClient):
    _conn_type = net.ServerID.admin
    _n = net.decode_key(settings.admin.n_key)
    _x = net.decode_key(settings.admin.x_key)

    def __init__(self):
        super(AdminCli, self).__init__()
        self.incoming_lookup = {
            
        }
        self.outgoing_lookup = {
            _msg.shutdown_request: 0
        }

    @asyncio.coroutine
    def _finalize_connection(self):
        # We need to establish the encryption...
        yield from crypto.establish_encryption_c2s(self, ord('a'), self._n, self._x)

    @asyncio.coroutine
    def shutdown(self, message):
        """Shuts the shard down"""
        netmsg = net.NetMessage(_msg.shutdown_request, message=message)
        yield from self.send_netstruct(netmsg)
