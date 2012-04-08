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

class EOFMsgError(ceof.Error):
    pass

class EOFMsg(object):
    """Be a message......"""

    def __init__(self, cmd="", eofid="", address="", group="", msg=""):
        self.cmd        = ceof.fillup(cmd, EOF_L_CMD)
        self.eofid      = ceof.fillup(eofid, EOF_L_ID)
        self.address    = ceof.fillup(address, EOF_L_ADDRESS)
        self.group      = ceof.fillup(group, EOF_L_GROUP)
        self.msgtext    = ceof.fillup(msg, EOF_L_MESSAGE)

    def get_message(self):
        return self.cmd + self.eofid + self.address + self.group + self.msgtext

    def set_message(self, message):
        if not len(message) == EOF_L_MSG_FULL:
            raise EOFMsgError("Message length wrong: %s != %s" % (len(message, EOF_L_MSG_FULL)))

        index = 0
        self.cmd        = message[index:index+EOF_L_CMD]
        index = index + EOF_L_CMD
        self.eofid      = message[index:index+EOF_L_ID)
        index = index + EOF_L_ID
        self.address    = message[index:index+EOF_L_ADRESS)
        index = index + EOF_L_ADDRESS
        self.group      = message[index:index+EOF_L_GROUP)
        index = index + EOF_L_GROUP
        self.msgtext    = ceof.fillup(msg, EOF_L_MESSAGE)

    message = property(get_message, set_message)
