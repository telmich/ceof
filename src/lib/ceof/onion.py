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
                chain = ceof.TransportProtocol.chain_to(route, peer, args.message)
                # Copy for debug
                orig_chain = list(chain)

                onion = cls(config.gpg_config_dir)
                onion_chain = onion.chain(chain)
                print("Onion chain: %s" % onion_chain)

            if args.send:
                first_link = orig_chain[-1]
                peer = first_link['peer']
                address = peer.random_address()
                log.debug("Sending generated message via %s to %s @ %s" % (str(orig_chain), str(peer), str(address)))

                # FIXME: use SenderServer Function!
                ceof.SenderServer.send(address, onion_chain)

    #def chain(self, chained_pkg):
    #def chain(self, chain, onion):
    def chain(self, chain):
        """Create an onion chain"""

        #log.debug(chained_pkg)
        #onion_chain = ""
        #lastaddr=""

        # Pakets left to be encrypted:

        # Get our packet to work on
        pkg = chain.pop()
        log.debug("Onion: Encrypting for %s, chain = %s" % (str(pkg), str(chain)))

        # If there is more, call us again
        if chain:
            inner_part = self.chain(chain)
        else:
            inner_part = ""

        cmd = pkg['cmd']

        # create empty core of the onion
        eofmsg = ceof.EOFMsg(cmd=cmd)

        # Nothing added when dropping the package
        if cmd == ceof.EOF_CMD_ONION_DROP:
            pass
        elif cmd == ceof.EOF_CMD_ONION_FORWARD:
            # FIXME: add noise?
            eofmsg.address = pkg['forward_address']

        elif cmd == ceof.EOF_CMD_ONION_MSG_DROP:
            # FIXME: add noise?
            eofmsg.msgtext = pkg['message']
            
        elif cmd == ceof.EOF_CMD_ONION_MSG_FORWARD:
            eofmsg.msgtext = pkg['message']
            eofmsg.address = pkg['forward_address']

        # We have the eofmsg and the inner part
        # Encrypt both and return

        onion = self.crypto.encrypt(str(eofmsg) + str(inner_part), pkg['peer'].fingerprint)

        return str(onion)

    def unpack(self, pkg):
        """Unpack an onion"""

        # FIXME: converting to string may fail if binary
        plaintext = str(self.crypto.decrypt(pkg))

        msg = plaintext[:ceof.EOF_L_MSG_FULL]
        rest = plaintext[ceof.EOF_L_MSG_FULL:]

        return (msg, rest)

