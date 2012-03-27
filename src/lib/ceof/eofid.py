# -*- coding: utf-8 -*-
#
# 2012 Nico Schottelius (nico-ceof at schottelius.org)
#
# This file is part of ceof.
#
# ceof is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ceof is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ceof. If not, see <http://www.gnu.org/licenses/>.
#
#
# Generate a new ID
#

import ceof
import logging
import random

log = logging.getLogger(__name__)

class EOFID(object):
    """Generate / manage IDs"""

    def __init__(self):
        self.seed = random.randint(0, ceof.EOF_ID_MAX)
        self.counter = self.seed

    def inc(self):
        """Increment and take care of overflow"""

        if self.counter == ceof.EOF_ID_MAX:
            self.counter = 0
        else:
            self.counter = self.counter + 1

    def get_next(self):
        """Return converted ID"""
        self.inc()

        return self.__class__.int_to_id(self.counter)

    @staticmethod
    def int_to_id(to_convert):
        """Convert int to ID"""
        index = ceof.EOF_L_ID-1
        eofid = []

        while index >= 0:
            part = ceof.EOF_ID_BASE**index

            # Fits in? Record and subtract
            if (to_convert - part) >= 0:
                times = int(to_convert / part)
                to_convert = to_convert - (times*part)
            else:
                times = 0

            # Append selected symbol
            eofid.append(ceof.EOF_ID_CHARS[times])
            #print("%s:%s" % (index, eofid))
            index = index - 1

        return "".join(eofid)

    @staticmethod
    def id_to_int(eofid):
        """Convert ID to int"""
        index = 0
        eofint = 0

        if len(eofid) > ceof.EOF_L_ID:
            raise ValueError("ID to long (%s > %s)" % (len(eofid), ceof.EOF_L_ID))

        while index < ceof.EOF_L_ID:
            character = eofid[index]
            part = ceof.EOF_ID_BASE**(ceof.EOF_L_ID-(index+1))
            position = ceof.EOF_ID_CHARS.index(character)

            to_add = (position * part)
            #print("%s * %s = %s" % (position, part, to_add))

            eofint = eofint + to_add
            index = index + 1

        return eofint
