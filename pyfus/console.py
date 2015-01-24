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
import atexit
import os, os.path
try:
    import readline
except ImportError:
    import pyreadline as readline
import sys

import adminsrv

_client = adminsrv.AdminCli()
_loop = None

def _quit(msg="shutdown by console"):
    _loop.call_soon_threadsafe(asyncio.async, _client.shutdown(msg))
    return False

_commands = {
    "shutdown": _quit,
    "quit": _quit,
}

def initialize():
    global _loop

    # Load/write readline history
    basepath = os.path.join(os.path.expanduser("~"), ".fus")
    if not os.path.isdir(basepath):
        os.makedirs(basepath)
    history = os.path.join(basepath, "history")
    readline.read_history_file(history)
    atexit.register(readline.write_history_file, history)

    # Start the AdminClient
    _loop = asyncio.get_event_loop()
    _loop.call_soon(asyncio.async, _client.start())

def parse_line():
    try:
        line = input("fus=> ")
    except EOFError:
        if __name__ == "__main__":
            _loop.stop()
            sys.exit()
        else:
            _quit(msg="console EOF")
            return False

    s = line.split()
    try:
        call = _commands[s[0].lower()]
    except LookupError:
        pass
    else:
        if len(s) > 1:
            return call(*s[1:])
        else:
            return call()
    return True

def run_forever():
    def loop():
        while True:
            if not parse_line():
                break

    # NOTE: This uses a thread pool. There appear to be some problems with deadlocks and scheduling
    #       if we simply "yield from" or call coroutines. Be certain to call_soon_threadsafe!
    future = _loop.run_in_executor(None, loop)
