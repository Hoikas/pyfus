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
from collections import OrderedDict
import datetime
import uuid

class _MemberNames(dict):
   def __init__(self):
      self._member_names = []

   def __setitem__(self, key, value):
      if key not in self:
         self._member_names.append(key)
      dict.__setitem__(self, key, value)


class _OrderedClass(type):
    """Records the order of creation of class attributes -- from PEP 3115"""
    @classmethod
    def __prepare__(metacls, name, bases):
       return _MemberNames()

    def __new__(cls, name, bases, classdict):
       result = type.__new__(cls, name, bases, dict(classdict))
       result._member_names = classdict._member_names
       return result


class DbTable(metaclass=_OrderedClass):
    def __init__(self, name):
        self._name = name

    @property
    def fields(self):
        print(self._member_names)
        for name in self._member_names:
            i = getattr(self, name, None)
            if isinstance(i, DbField):
                yield (name, i)

    def __str__(self):
        return self._name


class DbField:
    def __init__(self, name, default, nullable=False):
        self._name = name
        self._default = default
        self._nullable = nullable

        self._dirty = False
        self._value = default

    def __call__(self, value=None, dirty=True):
        if value is None:
            return self._value
        else:
            self._value = value
            self._dirty = dirty

    @abc.abstractmethod
    def field_type(self, engine):
        pass

    def __repr__(self):
        return self._value

    def __str__(self):
        return self._name


class DbIntField(DbField):
    def __init__(self, name, default=0, unsigned=False, auto_increment=False, primary_key=False, nullable=False):
        super().__init__(name, default, nullable)
        self._unsigned = unsigned
        self._auto_increment = auto_increment
        self._primary_key = primary_key

    def field_type(self, engine):
        field = "INTEGER"
        if self._primary_key:
            field += " PRIMARY KEY"
        if self._auto_increment:
            # yeah, yeah...
            if engine == "sqlite3":
                field += " AUTOINCREMENT"
            else:
                field += " AUTO_INCREMENT"
        if self._unsigned and engine != "sqlite3":
            field += " UNSIGNED"
        if not self._nullable:
            field += " NOT"
        field += " NULL"
        return field


class DbDateTimeField(DbIntField):
    def __init__(self, name, nullable=False):
        super().__init__(name, unsigned=True, nullable=nullable)

    def __call__(self, value=None, dirty=True):
        if value is None:
            return datetime.datetime.utcfromtimestamp(super().__call__())
        else:
            super().__call__(value.timestamp(), dirty)


class DbStringField(DbField):
    def __init__(self, name, default="", size=-1, varying=True, nullable=False):
        super().__init__(name, default, nullable)
        self._max_size = size
        self._varchar = varying

    def field_type(self, engine):
        if self._max_size == -1:
            field = "TEXT"
        elif self._varchar:
            field = "VARCHAR({})".format(self._max_size)
        else:
            field = "CHAR({})".format(self._max_size)

        if self._nullable:
            field += " NULL"
        else:
            field += " NOT NULL"
        return field


class DbBlobField(DbStringField):
    def __init__(self, name, default="", nullable=False):
        super().__init__(name, default, -1, False, nullable)

    def __call__(self, value=None, dirty=True):
        if value is None:
            return base64.b64decode(super().__call__(None))
        else:
            super().__call__(base64.b64encode(value), dirty)


class DbUuidField(DbStringField):
    def __init__(self, name, nullable=False):
        super().__init__(name, uuid.UUID(int=0).bytes_le, size=16, varying=False, nullable=nullable)

    def __call__(self, value=None, dirty=True):
        if value is None:
            return uuid.UUID(bytes_le=super().__call__())
        else:
            super().__call__(value.bytes_le, dirty)
