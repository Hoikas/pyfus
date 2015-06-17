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
import os.path

import dbal
import settings

class _VaultNodesTable(dbal.DbTable):
    idx = dbal.DbIntField("idx", unsigned=True, auto_increment=True, primary_key=True)
    create_time = dbal.DbDateTimeField("CreateTime", nullable=True)
    modify_time = dbal.DbDateTimeField("ModifyTime", nullable=True)
    create_age_name = dbal.DbStringField("CreateAgeName", size=64, nullable=True)
    create_age_uuid = dbal.DbUuidField("CreateAgeUuid", nullable=True)
    creator_uuid = dbal.DbUuidField("CreatorUuid", nullable=True)
    creator_idx = dbal.DbIntField("CreatorIdx", unsigned=True, nullable=True)
    node_type = dbal.DbIntField("NodeType", unsigned=True, nullable=True)
    int32_1 = dbal.DbIntField("Int32_1", nullable=True)
    int32_2 = dbal.DbIntField("Int32_2", nullable=True)
    int32_3 = dbal.DbIntField("Int32_3", nullable=True)
    int32_4 = dbal.DbIntField("Int32_4", nullable=True)
    uint32_1 = dbal.DbIntField("UInt32_1", unsigned=True, nullable=True)
    uint32_2 = dbal.DbIntField("UInt32_2", unsigned=True, nullable=True)
    uint32_3 = dbal.DbIntField("UInt32_3", unsigned=True, nullable=True)
    uint32_4 = dbal.DbIntField("UInt32_4", unsigned=True, nullable=True)
    uuid_1 = dbal.DbUuidField("Uuid_1", nullable=True)
    uuid_2 = dbal.DbUuidField("Uuid_2", nullable=True)
    uuid_3 = dbal.DbUuidField("Uuid_3", nullable=True)
    uuid_4 = dbal.DbUuidField("Uuid_4", nullable=True)
    string64_1 = dbal.DbStringField("String64_1", size=64, nullable=True)
    string64_2 = dbal.DbStringField("String64_2", size=64, nullable=True)
    string64_3 = dbal.DbStringField("String64_3", size=64, nullable=True)
    string64_4 = dbal.DbStringField("String64_4", size=64, nullable=True)
    string64_5 = dbal.DbStringField("String64_5", size=64, nullable=True)
    string64_6 = dbal.DbStringField("String64_6", size=64, nullable=True)
    istring64_1 = dbal.DbStringField("IString64_1", size=64, nullable=True)
    istring64_2 = dbal.DbStringField("IString64_2", size=64, nullable=True)
    text_1 = dbal.DbStringField("Text_1", nullable=True)
    text_2 = dbal.DbStringField("Text_2", nullable=True)
    blob_1 = dbal.DbBlobField("Blob_1", nullable=True)
    blob_2 = dbal.DbBlobField("Blob_2", nullable=True)


class FusDatabase(dbal.DbDatabase):
    vault_nodes = _VaultNodesTable("VaultNodes")

    @asyncio.coroutine
    def connect_ini(self):
        """Connects to the database specified in fus.ini"""

        db = settings.db
        if db.engine == "sqlite3":
            file = os.path.normpath(os.path.expanduser(db.name))
            print(file)
            yield from self.connect("sqlite3", path=file)
