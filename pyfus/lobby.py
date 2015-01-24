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

class LobbySrv(net.ServerBase):
    _conn_type = ord('l')

    def __init__(self):
        super(LobbySrv, self).__init__()
        self._client_tasks = []

    @asyncio.coroutine
    def accept_client(self, client):
        # This should really raise an exception, but that exposes an attack vector.
        # Let's just nuke this foolish client.
        client.writer.close()

    def shutdown(self):
        # First, kill off the listen server...
        self._server.close()
        asyncio.wait(self._server.wait_closed())

        # Now nuke all client sessions.
        # NOTE: By doing this, we will implicitly nuke any fus srv2srv clients
        #       Yes, I'm looking at you, AdminClient
        for i in self._client_tasks:
            i.cancel()
        del self._client_tasks[:]

        # We aren't dead yet... The loop still needs to run and raise the exceptions. Anything that
        # is shielded will need to finish (eg database transactions). Then, the loop will end, and we
        # go p00f, p00f, a p00fing
        asyncio.get_event_loop().stop()

    def start(self, loop):
        host = settings.lobby.host
        port = settings.lobby.port
        self._server = loop.run_until_complete(asyncio.start_server(self._on_client_connect, host=host, port=port))

    def _on_client_connect(self, reader, writer):
        cli = type("Client", tuple(), {"reader": reader, "writer": writer})

        try:
            # TODO: impose a timeout here to defeat slowloris
            header = yield from net.read_netstruct(reader, net.connection_header)
        except ConnectionError:
            return

        srv = net.fetch_server(header.conn_type)
        task = asyncio.async(srv.accept_client(cli))
        self._client_tasks.append(task)


# Register this server so things actually happen
net.register_server(LobbySrv)
