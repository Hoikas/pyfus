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

# Some requisite imports to ensure everything is set up correctly.
# NOTE: We *must* include all server modules here so that they register themselves.
import gatesrv, lobby
import settings

# Things that we actually use
import net

def _init_event_loop():
    """Initializes the correct event loop for our platform"""

    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    return loop


if __name__ == "__main__":
    # The very first thing we want to do is initialize the event loop so that the individual servers
    # have something that they can register their crap with.
    loop = _init_event_loop()

    # Now, we loop through all of the servers that we have and tell them that it's party time.
    # NOTE that we aren't doing much listen/accept logic here. That happens in the lobby...
    for i in net.all_servers():
        i.start(loop)

    # And now, we run the event loop forever and ever...
    try:
        loop.run_forever()
    finally:
        loop.close()
