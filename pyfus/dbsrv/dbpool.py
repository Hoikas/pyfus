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
import concurrent.futures
import queue

from .dbfus import FusDatabase
import settings

class _DbConnectionList(list):
    def __init__(self, size):
        self._pops = queue.Queue()
        super().extend([None] * size)

    def append(self, value):
        if not self._pops.empty():
            future = self._pops.get_nowait()
            future.set_result(value)
        else:
            super().append(value)

    @asyncio.coroutine
    def pop(self):
        base = super()
        if base:
            return base.pop()
        else:
            future = asyncio.Future()
            self._pops.put_nowait(future)
            return (yield from future)


class _DbConnectionMgr:
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._pool._connections.append(self._conn)
        # this ensures stolen copies become invalid
        self._conn = None

    def __getattr__(self, attr):
        return getattr(self._conn, attr)


class DbPool:
    def __init__(self):
        size = settings.db.pool_size

        self.executor = concurrent.futures.ThreadPoolExecutor(size)
        self._connections = _DbConnectionList(size)

    @asyncio.coroutine
    def db_connection(self):
        conn = yield from self._connections.pop()
        if conn is None:
            conn = FusDatabase()
            yield from conn.connect_ini()
        return _DbConnectionMgr(conn, self)
