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
        if args.create and not args.message:
            raise OnionError("Requiring message and peer for onion create")

        if args.onion_to:
            peer = ceof.Peer.from_disk(config.peer_dir, args.onion_to)
            route = ceof.Transport.route_to(config.peer_dir, peer, ceof.EOF_L_ROUTERS)
            onion = ceof.Transport.chained_pkg(route, peer, "test")
            print(onion)

    @staticmethod
    def onion_chain(chained_pkg):
        """Create onion chain"""

        onion_chain = ""
        for part in chained_pkg:
            onion_chain = onion_pkg(pkg, onion_chain)

        return onion_chain

    @staticmethod
    def onion_pkg(pkg, onion, lastaddr):
        """Create an onion"""
        if pkg['cmd'] == ceof.EOF_CMD_ONION_DROP:
            core = cmd + noise(EOF_L_ID + EOF_L_ADDRESS + EOF_L_GROUP + EOF_L_MESSAGE)

        elif pkg['cmd'] == ceof.EOF_CMD_ONION_FORWARD:
            address = ceof.fillup(lastaddr, EOF_L_ADDRESS)

            core = cmd + noise(EOF_L_ID) + address + noise(EOF_L_GROUP + EOF_L_MESSAGE)

        elif pkg['cmd'] == ceof.EOF_CMD_ONION_MSG_DROP:
            message = ceof.fillup(lastaddr, pkg['message'])
            core = cmd + eof_id + noise(EOF_L_ADDRESS + EOF_L_GROUP) + message
            
        elif pkg['cmd'] == ceof.EOF_CMD_ONION_MSG_FORWARD:
            address = ceof.fillup(lastaddr, EOF_L_ADDRESS)
            message = ceof.fillup(lastaddr, pkg['message'])

            core = cmd + eof_id + address + noise(EOF_L_GROUP) + message
            
        return crypto.encrypt(core + onion, pkg['peer']['fingerprint'])

    def _get_noise_message(self):
        """Get next noise message"""
        return self._noise.get()
