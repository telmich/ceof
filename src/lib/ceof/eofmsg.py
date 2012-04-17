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

import ceof
import logging

log = logging.getLogger(__name__)

class EOFMsgError(ceof.Error):
    pass

class EOFMsg(object):
    """Be a message......"""

    def __init__(self, cmd="", eofid="", address="", group="", msgtext=""):
        self.version    = "0"

        self.cmd        = cmd
        self.eofid      = eofid
        self.address    = address
        self.group      = group
        self.msgtext    = msgtext

    def __str__(self):
        return self.message

    def get_message(self):
        return self.version + self.cmd + self.eofid + self.address + self.group + self.msgtext

    def set_message(self, message):
        if not len(message) == ceof.EOF_L_MSG_FULL:
            raise EOFMsgError("Message length (%s) should be %s" % (len(message), ceof.EOF_L_MSG_FULL))

        index = 0
        self.cmd        = message[index:index+ceof.EOF_L_CMD]
        index = index + ceof.EOF_L_CMD
        self.eofid      = message[index:index+ceof.EOF_L_ID]
        index = index + ceof.EOF_L_ID
        self.address    = message[index:index+ceof.EOF_L_ADRESS]
        index = index + ceof.EOF_L_ADDRESS
        self.group      = message[index:index+ceof.EOF_L_GROUP]
        index = index + ceof.EOF_L_GROUP
        self.msgtext    = message[index:index+ceof.EOF_L_MESSAGE]

    def get_version(self):
        return self._version

    def set_version(self, version):
        self._version = ceof.fill_and_trim(version, ceof.EOF_L_VERSION)

    def get_cmd(self):
        return self._cmd

    def set_cmd(self, cmd):
        self._cmd = ceof.fill_and_trim(cmd, ceof.EOF_L_CMD)

    def get_eofid(self):
        return self._eofid

    def set_eofid(self, eofid):
        self._eofid = ceof.fill_and_trim(eofid, ceof.EOF_L_ID)

    def get_address(self):
        return self._address

    def set_address(self, address):
        self._address = ceof.fill_and_trim(address, ceof.EOF_L_ADDRESS)

    def get_group(self):
        return self._group

    def set_group(self, group):
        self._group = ceof.fill_and_trim(group, ceof.EOF_L_GROUP)

    def get_msgtext(self):
        return self._msgtext

    def set_msgtext(self, msgtext):
        self._msgtext = ceof.fill_and_trim(msgtext, ceof.EOF_L_MESSAGE)

    version = property(get_version, set_version)
    cmd = property(get_cmd, set_cmd)
    eofid = property(get_eofid, set_eofid)
    address = property(get_address, set_address)
    group = property(get_group, set_group)
    message = property(get_message, set_message)
    msgtext = property(get_msgtext, set_msgtext)
