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

import ctypes
import sys

if sys.platform == "win32":
    _openssl = ctypes.CDLL("libeay32.dll")
else:
    _openssl = ctypes.CDLL("libcrypto.so")

BN_new = _openssl.BN_new
BN_free = _openssl.BN_free
BN_num_bits = _openssl.BN_num_bits
BN_num_bytes = lambda bn: int((BN_num_bits(bn) + 7) / 8)
BN_generate_prime_ex = _openssl.BN_generate_prime_ex
BN_bn2bin = _openssl.BN_bn2bin

RAND_bytes = _openssl.RAND_bytes
RAND_seed = _openssl.RAND_seed
if sys.platform == "win32":
    RAND_screen = _openssl.RAND_screen
else:
    def RAND_screen():
        raise RuntimeError("Platform not supported")
