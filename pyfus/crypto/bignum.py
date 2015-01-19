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

from . import openssl

def generate_prime(bits):
    prime = openssl.BN_new()
    assert openssl.BN_generate_prime_ex(prime, bits, 1, None, None, None, None) == 1
    buf = bytes(openssl.BN_num_bytes(prime))
    assert openssl.BN_bn2bin(prime, buf) != 0
    openssl.BN_free(prime)
    return int.from_bytes(buf, byteorder="big")
