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
import ceof.noise
import logging

log = logging.getLogger(__name__)

class EOFMsgError(ceof.Error):
    pass

class EOFMsg(object):
    """Be a message......"""

    def __init__(self, cmd="", eofid="", address="", group="", msgtext=""):
        self._version    = "0"

        self._cmd        = cmd
        self._eofid      = eofid
        self._address    = address
        self._group      = group
        self._msgtext    = msgtext

    def __str__(self):
        return self.message

    def __repr__(self):
        return ("<EOFMsg version=%s,cmd=%s, eofid=%s, address=%s, group=%s, msgtext=%s> " % (self.version , self.cmd , self.eofid , self.address , self.group , self.msgtext))

    def get_message(self):
        return self.version + self.cmd + self.eofid + self.address + self.group + self.msgtext

    def set_message(self, message):
        if not len(message) == ceof.EOF_L_MSG_FULL:
            raise EOFMsgError("Message length (%s) should be %s" % (len(message), ceof.EOF_L_MSG_FULL))

        index = 0
        self.version    = message[index:index+ceof.EOF_L_VERSION]
        index = index + ceof.EOF_L_VERSION
        self.cmd        = message[index:index+ceof.EOF_L_CMD]
        index = index + ceof.EOF_L_CMD
        self.eofid      = message[index:index+ceof.EOF_L_ID]
        index = index + ceof.EOF_L_ID
        self.address    = message[index:index+ceof.EOF_L_ADDRESS]
        index = index + ceof.EOF_L_ADDRESS
        self.group      = message[index:index+ceof.EOF_L_GROUP]
        index = index + ceof.EOF_L_GROUP
        self.msgtext    = message[index:index+ceof.EOF_L_MESSAGE]

    def noisify(self, noise):
        """Insert noise into unused fields"""

        log.debug("Inserting noise into EOFMsg")
        index = 0

        if not self.eofid:
            self.eofid      = noise[index:index+ceof.EOF_L_ID]
            index = index + ceof.EOF_L_ID

        if not self.address:
            self.address      = noise[index:index+ceof.EOF_L_ADDRESS]
            index = index + ceof.EOF_L_ADDRESS

        # Group is currently unused, pad it with noise
        self.group      = noise[index:index+ceof.EOF_L_GROUP]
        index = index + ceof.EOF_L_GROUP

        if not self.msgtext:
            self.msgtext      = noise[index:index+ceof.EOF_L_MESSAGE]
            index = index + ceof.EOF_L_MESSAGE

        log.debug("Used %d Bytes of noise" % (index))

    @classmethod
    def chain_noisified(cls, route, peer, message, noise_dir):
        """Create chain including fields being noisified"""

        noise = ceof.noise.Filesystem(noise_dir)
        chain = cls.chain_plain(route, peer, message)

        for proxy_pkg in chain:
            noise_block = noise.get_next_block()
            proxy_pkg['eofmsg'].noisify(noise_block)

        return chain

    @classmethod
    def chain_plain(cls, route, peer, message):
        """Create a chain of eofmsg that is used for encryption later"""

        # First peer that receives is the last one that last decrypts
        chain = []
        for proxy in route:
            proxy_pkg = {}
            proxy_pkg['peer'] = proxy

            if proxy == peer and message:
                """If there is no message, we create a chain of noise => no recipient"""

                if len(chain) == 0:
                    """First peer"""
                    proxy_pkg['eofmsg']         = cls(cmd=ceof.EOF_CMD_ONION_MSG_DROP)
                else:
                    proxy_pkg['eofmsg']         = cls(cmd=ceof.EOF_CMD_ONION_MSG_FORWARD)
                    proxy_pkg['eofmsg'].address = chain[-1]['peer'].random_address()

                proxy_pkg['eofmsg'].msgtext     = message
            else:
                if len(chain) == 0:
                    """First peer"""
                    proxy_pkg['eofmsg']         = cls(cmd=ceof.EOF_CMD_ONION_DROP)
                else:
                    proxy_pkg['eofmsg']         = cls(cmd=ceof.EOF_CMD_ONION_FORWARD)
                    proxy_pkg['eofmsg'].address = chain[-1]['peer'].random_address()

            chain.append(proxy_pkg)

        return chain

    def get_version(self):
        return self._version

    def set_version(self, version):
        # Version cannot be overwritten from outside
        version = "0"
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
