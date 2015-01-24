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

import argparse
import configparser
import os.path
import sys
import uuid

# This is like a default fus.ini
_default_config = {
    "admin": {
        "k_key": "",
        "n_key": "",
        "x_key": "",
    },

    "auth": {
        "restrict_logins": False,
        "k_key": "",
        "n_key": "",
    },

    "game": {
        "k_key": "",
        "n_key": "",
    },

    "gatekeeper": {
        "authsrv_ip": "127.0.0.1",
        "filesrv_ip": "127.0.0.1",
        "k_key": "",
        "n_key": "",
    },

    "lobby": {
        "host": "0.0.0.0",
        "port": 14617,
    },

    "product": {
        "build_id": 0,
        "uuid": uuid.UUID("ea489821-6c35-4bd0-9dae-bb17c585e680"),
    },

    "shard": {
        "hood_instance": "Neighborhood",
        "default_hood_name": "FusRoDah",
        "default_hood_pop": 50,
    }
}

# fus command-line argument parsing
_parser = argparse.ArgumentParser(prog="fus")
_parser.add_argument("--restrict-logins", action="store_true", default="False", help="disallow logins by normal users (super-users only)")
_parser.add_argument("fus_ini", metavar="fus.ini", default="fus.ini", nargs="?", help="path to the fus configuration file")

# First, we need to parse the command line arguments to uncover where fus.ini is...
_args = _parser.parse_args()

# Now, load fus.ini
_config = configparser.ConfigParser()
if os.path.isfile(_args.fus_ini):
    _config.read(_args.fus_ini)
elif __name__ != "__main__":
    print("fus configuration file '{}' not found.".format(_args.fus_ini))
    print("please configure fus before attempting to start the server.")
    sys.exit()


class _IniSection:
    def __init__(self, name, d):
        for key, value in d.items():
            if _config.has_option(name, key):
                if isinstance(value, bool):
                    theValue = _config.getboolean(name, key)
                elif isinstance(value, int):
                    theValue = _config.getint(name, key)
                elif isinstance(value, uuid.UUID):
                    theValue = uuid.UUID(_config.get(name, key))
                else:
                    theValue = _config.get(name, key)
            else:
                theValue = value
            setattr(self, key, theValue)


# Create variables for each section
for _key, _value in _default_config.items():
    globals()[_key] = _IniSection(_key, _value)


# If we're running as __main__, then let's spit out a sample configuration...
if __name__ == "__main__":
    with open(_args.fus_ini, "w") as f:
        sys.stdout, stdout = f, sys.stdout
        for key, value in sorted(_default_config.items()):
            print("[{}]".format(key))
            for name, var in sorted(value.items()):
                print("{} = {}".format(name, var))
            print()
        sys.stdout = stdout
