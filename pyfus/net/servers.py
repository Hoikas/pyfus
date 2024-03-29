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

import abc
import base64

import util

_servers = {}

# Some konstants
_c2s_connect = 0
_s2c_encrypt = 1

class ServerBase(abc.ABC):
    def __init__(self, log=None):
        self.clients = util.LinkedList()

        if log is None:
            self._log = util.find_log(self.__class__.__name__)
        else:
            self._log = log
        self.log_debug = self._log.debug
        self.log_info = self._log.info
        self.log_warn = self._log.warn
        self.log_error = self._log.error

    @abc.abstractmethod
    def accept_client(self, client):
        pass

    def start(self, loop):
        pass


def all_servers():
    """Enumerates all registered servers"""
    for i in _servers.values():
        yield i

def decode_key(key):
    return int.from_bytes(base64.b64decode(key), byteorder="big")

def fetch_server(conn_type):
    """Fetches a specific server type"""
    return _servers[conn_type]

def register_server(cls):
    """Registers a server class"""
    if (issubclass(cls, ServerBase)):
        if cls._conn_type not in _servers:
            _servers[cls._conn_type] = cls()
    else:
        raise RuntimeError("`{}` is not a valid server class".format(cls))