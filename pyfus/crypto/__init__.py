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

"""So just why exactly is there yet another OpenSSL binding. In pyfus, of all places?
Simple, the Tsar responds, The stupid ssl module and the even stupider pyopenssl don't expose bignum.
But why? you ask. Python ints are arbitarily sized.
Ah, young grasshopper, the size is only a side issue, the Tsar answers knowingly. The real problem
is that we need to generate big prime numbers, and some people don't want to do this at home.
And all were amazed at the sense.
"""

from .bignum import *
from .netio import *
from .rand import *
