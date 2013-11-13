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
import ceof.eofmsg

import logging
import os.path
import pprint
import random
import re

log = logging.getLogger(__name__)

class OnionError(ceof.Error):
    pass

class Onion(object):
    """Onions - the core"""

    def __init__(self, gpg_config_dir):
        self.crypto = ceof.Crypto(gpg_config_dir)

    @classmethod
    def commandline(cls, args, config):
        if args.message and not args.name:
            raise OnionError("Requiring peer name for onion")

        if args.send and not args.message:
            raise OnionError("Requiring message for message sending...")

        for repeat in range(args.repeat_count):
            if args.message:
                peer = ceof.Peer.from_disk(config.peer_dir, args.name)
                route = ceof.TransportProtocol.route_to(config.peer_dir, peer, ceof.EOF_L_ADDITIONAL_PEERS)
                chain = ceof.EOFMsg.chain_noisified(route, peer, args.message, config.noise_dir)

                if args.plain:
                    print("Plain Onion:")
                    pprint.pprint(chain)

                # Copy for debug
                orig_chain = list(chain)

                onion = cls(config.gpg_config_dir)
                onion_chain = onion.chain(chain)
                print("Onion chain:\n%s" % onion_chain)

            if args.send:
                first_link = orig_chain[-1]
                peer = first_link['peer']
                address = peer.random_address()
                log.info("Sending generated message via %s to %s @ %s" % (str(orig_chain), str(peer), str(address)))

                ceof.SenderServer.send(address, onion_chain)

    @classmethod
    def create(cls, config, peername, message):

        peer = ceof.Peer.from_disk(config.peer_dir, peername)
        route = ceof.TransportProtocol.route_to(config.peer_dir, peer, ceof.EOF_L_ADDITIONAL_PEERS)
        chain = ceof.EOFMsg.chain_noisified(route, peer, message, config.noise_dir)

        # chain will be modified below, get the address now
        first_link      = chain[-1]
        first_peer      = first_link['peer']
        first_address   = peer.random_address()

        onion = cls(config.gpg_config_dir)
        onion_chain = onion.chain(chain)

        return (first_address, onion_chain)

    def chain(self, chain):
        """Create an onion chain"""

        # Get our packet to work on
        pkg = chain.pop()
        log.debug("Onion: Encrypting for %s, chain = %s" % (str(pkg), str(chain)))

        # If there is more, call us again
        if chain:
            inner_part = self.chain(chain)
        else:
            inner_part = ""

        eofmsg = pkg['eofmsg']
        fingerprint = pkg['peer'].fingerprint

        onion = self.crypto.encrypt(str(eofmsg) + str(inner_part), fingerprint)

        return str(onion)

    def unpack(self, pkg):
        """Unpack an onion"""

        # FIXME: converting to string may fail if binary
        plaintext = str(self.crypto.decrypt(pkg))

        msg = plaintext[:ceof.EOF_L_MSG_FULL]
        rest = plaintext[ceof.EOF_L_MSG_FULL:]

        return (msg, rest)

