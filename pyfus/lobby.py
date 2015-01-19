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

import net
import settings

fields = net.fields
connection_header = (
    (fields.integer, "conn_type", 1),
    (fields.integer, "size", 2),
    (fields.integer, "build_id", 4),
    (fields.integer, "build_type", 4),
    (fields.integer, "branch_id", 4),
    (fields.uuid, "product", 1),
)


class LobbySrv(net.ServerBase):
    # Most servers have a numerical ID... But the lobby does not. Let's cheat.
    _conn_type = "lobby"

    def accept_client(self, client):
        raise RuntimeError("LobbySrv cannot accept clients. It listens for connections!")

    def start(self, loop):
        host = settings.lobby.host
        port = settings.lobby.port
        loop.run_until_complete(asyncio.start_server(self._on_client_connect, host=host, port=port))

    def _on_client_connect(self, reader, writer):
        header = yield from net.read_netstruct(reader, connection_header)
        print(str(header)) # FIXME: temp debugging

        cli = type("Client", tuple(), {"reader": reader, "writer": writer})
        srv = net.fetch_server(header.conn_type)
        # NOTE: We have to schedule the accept to happen later so we don't halt the listen loop
        #       forever. Python is actually smart enough to detect this and will actually nuke the
        #       accept_client if we _don't_ schedule it.
        asyncio.async(srv.accept_client(cli))


# Register this server so things actually happen
net.register_server(LobbySrv)
