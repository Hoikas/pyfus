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
import copy
import functools
import importlib

from . import table

_SUPPORTED_ENGINES = {"sqlite3"}
_SUPPORTED_PARAMSTYLE = {"format", "qmark"}

class DbDatabase:
    def __init__(self, executor=None):
        self._executor = executor
        self._connection = None

    def __del__(self):
        if self._connection is not None:
            self._connection.close()

    @asyncio.coroutine
    def connect(self, engine, name="fusrodah", host="localhost", user="fus", password="", path="~/.fus/vault.db"):
        if engine not in _SUPPORTED_ENGINES:
            raise RuntimeError("'{}' is not a supported database engine".format(engine))
        self._engine = importlib.import_module(engine)

        # Threads have to be able to share the engine module...
        assert self._engine.threadsafety > 0
        # Make sure we support the paramstyle
        assert self._engine.paramstyle in _SUPPORTED_PARAMSTYLE

        # As you can see, we are quite lazy...
        if self._engine.paramstyle == "qmark":
            self._param = "?"
        else:
            self._param = "%s"

        # Per-engine connection calls, just cause
        if engine == "sqlite3":
            # We deliberately disable thread checking here because the DB Pool ensures that only
            # one thread is ever touching a connection... This is Python, it ought to just work(TM),
            # but, like the rest of DB-API 2.0, it's full of gotchas.
            call = functools.partial(self._engine.connect, path, check_same_thread=False)

        # Run the blocking connection thing in a thread
        loop = asyncio.get_event_loop()
        self._connection = yield from loop.run_in_executor(self._executor, call)

    def initialize(self):
        """Ensures all tables are created on this database. Note that tables are NOT upgraded if the
           schema has changed! That's your problem, not ours..."""
        engine = self._engine.__name__

        # Just in case you're wondering, this is NOT a coroutine because it executes long before the
        # event loops starts pumping. We can get away with blocking at this stage in the game :)
        with self._connection as cursor:
            for table in self.tables:
                command = "CREATE TABLE IF NOT EXISTS `{}` (\n".format(table)
                columns = ",\n".join(["    `{}` {}".format(str(field), field.field_type(engine)) for code_name, field in table.fields])
                query = command + columns + "\n)"
                cursor.execute(query)

    @property
    def tables(self):
        for i in self.__class__.__dict__.values():
            if isinstance(i, table.DbTable):
                yield i


class _DbRow:
    def __init__(self, db, table, result):
        self._db = db

        for name, field in table.fields:
            if name in result:
                myField = copy.copy(field)
                myField._value = result[name]
                setattr(self, name, myField)

    @asyncio.coroutine
    def update(self):
        pass
