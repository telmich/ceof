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
import os.path
import random
import re

log = logging.getLogger(__name__)

class OnionError(ceof.Error):
    pass

class Onion(object):
    """Onions - the core"""

    def __init__(self, config):
        self.noise = ceof.Noise(config.noise_dir)

    @classmethod
    def commandline(cls, args, config):
        if args.message and not args.name:
            raise OnionError("Requiring peer name for onion")

        if args.message:
            peer = ceof.Peer.from_disk(config.peer_dir, args.name)
            route = ceof.TransportProtocol.route_to(config.peer_dir, peer, ceof.EOF_L_ROUTERS)
            chain = ceof.TransportProtocol.chained_pkg(route, peer, args.message)
            onion = cls.onion_chain(chain)
            print(chain)

    @classmethod
    def onion_chain(cls, chained_pkg):
        """Create onion chain"""

        print(chained_pkg)
        onion_chain = ""
        lastaddr=""
        for pkg in chained_pkg:
            print(pkg)
            onion_chain = cls.onion_pkg(pkg, onion_chain, lastaddr)
            lastaddr = pkg['address']
            print(onion_chain)

        return onion_chain

    @staticmethod
    def onion_pkg(pkg, onion, lastaddr):
        """Create an onion"""

        cmd = pkg['cmd']

        # empty core of the onion
        eofmsg = ceof.EOFMsg(cmd=cmd)
        eofmsg.group = "muuu"
        print("msg: " + str(eofmsg) + "x")

        # Nothing added when dropping the package
        if cmd == ceof.EOF_CMD_ONION_DROP:
            pass
        elif cmd == ceof.EOF_CMD_ONION_FORWARD:
            address = ceof.fillup(lastaddr, EOF_L_ADDRESS)

            core = cmd + ceof.fillup(ceof.EOF_L_ID) + address + ceof.fillup(ceof.EOF_L_GROUP + ceof.EOF_L_MESSAGE)

        elif cmd == ceof.EOF_CMD_ONION_MSG_DROP:
            message = pkg['message']
            core = cmd + eof_id + ceof.fillup(EOF_L_ADDRESS + EOF_L_GROUP) + message
            
        elif cmd == ceof.EOF_CMD_ONION_MSG_FORWARD:
            address = ceof.fillup(lastaddr, EOF_L_ADDRESS)
            message = pkg['message']

            core = cmd + eof_id + address + ceof.fillup(EOF_L_GROUP) + message
            
        return crypto.encrypt(core + onion, pkg['peer']['fingerprint'])

    def _get_noise_message(self):
        """Get next noise message"""
        return self._noise.get()
