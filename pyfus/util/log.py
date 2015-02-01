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

import os, os.path
import time

import settings

_logs = {}

class _LogLevel:
    debug = 0
    info = 1
    warn = 2
    warning = 2
    error = 3


class _LogFile:
    """Because the logging module tries to do way too much"""

    def __init__(self, name):
        self._logkey = name
        self._logname = "{}.log".format(name)
        logpath = os.path.normpath(os.path.expanduser(settings.log.path))
        if not os.path.isdir(logpath):
            os.makedirs(logpath)
        logpath = os.path.join(logpath, self._logname)
        self._handle = open(logpath, mode='w', encoding="utf8")
        self._writeline("BEGIN '{}'".format(self._logname))

    def __del__(self):
        self._writeline("END '{}'".format(self._logname))
        self._handle.close()

    def debug(self, msg, *args, leader=None):
        if _level == _LogLevel.debug:
            self._writeline(msg, *args, levelStr="DBG", leader=leader)

    def info(self, msg, *args, leader=None):
        if _level <= _LogLevel.info:
            self._writeline(msg, *args, levelStr="INF", leader=leader)

    def warn(self, msg, *args, leader=None):
        if _level <= _LogLevel.warning:
            self._writeline(msg, *args, levelStr="WRN", leader=leader)

    def error(self, msg, *args, leader=None):
        if _level <= _LogLevel.error:
            self._writeline(msg, args, levelStr="ERR", leader=leader)

    def _writeline(self, line, *args, levelStr=None, leader=None):
        if len(args) > 0:
            line = line.format(*args)

        now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        if levelStr is None:
            theLine = "[{}] {}\n".format(now, line)
        elif leader is None:
            theLine = "[{}] {}: {}\n".format(now, levelStr, line)
        else:
            theLine = "[{}] {}: [{}] {}\n".format(now, levelStr, leader, line)
        self._handle.write(theLine)
        self._handle.flush()


def find_log(name):
    try:
        lawg = _logs[name]
    except LookupError:
        lawg = _LogFile(name)
        _logs[name] = lawg
    finally:
        return lawg

# Sanity check the log level
_level = getattr(_LogLevel, settings.log.level, None)
if _level is None:
    raise RuntimeError("Invalid log level '{}' specified in fus.ini".format(settings.log.level))
