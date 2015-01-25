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

from net import fields

connection_header = (
    (fields.integer, "size", 4),
    (fields.integer, "build_id", 4),
    (fields.integer, "server_type", 4),
)

build_request = (
    (fields.integer, "trans_id", 4),
)
build_reply = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "result", 4),
    (fields.integer, "build_id", 4),
)
