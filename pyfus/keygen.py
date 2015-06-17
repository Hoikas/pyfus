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

import base64
import crypto

from constants import DiffieHellmanG

gValues = {
    (None, "admin"): DiffieHellmanG.admin,
    ("Server.Auth", "auth"): DiffieHellmanG.auth,
    (None, "db"): DiffieHellmanG.db,
    ("Server.Game", "game"): DiffieHellmanG.game,
    ("Server.Gate", "gatekeeper"): DiffieHellmanG.gatekeeper,
}

def generate_keyset(cliname, srvname, gValue):
    def _base64(value):
        bstr = base64.b64encode(value)
        return bstr.decode(encoding="utf8")

    k, n, x = crypto.generate_keys(gValue)
    serverini, fusini = [], []

    fusini.append("[{}]".format(srvname))
    fusini.append("k_key = {}".format(_base64(k)))
    fusini.append("n_key = {}".format(_base64(n)))

    if cliname:
        serverini.append("{}.N \"{}\"".format(cliname, _base64(n)))
        serverini.append("{}.X \"{}\"".format(cliname, _base64(x)))
    else:
        # This is a srv2srv connection, so we need all the keys in fus.ini
        fusini.append("x_key = {}".format(_base64(x)))
    return serverini, fusini

if __name__ == "__main__":
    print("Generating keys... You might want to grab a snack.")
    print()

    serverini, fusini = [], []
    for names, gValue in gValues.items():
        s2, f2 = generate_keyset(names[0], names[1], gValue)
        serverini.extend(s2)
        fusini.extend(f2)

    print("Okay! All set. Here's what you need to add to your configuration...")
    print("Plasma Client server.ini:")
    for i in serverini:
        print(i)
    print()
    print("Server fus.ini:")
    for i in fusini:
        print(i)
