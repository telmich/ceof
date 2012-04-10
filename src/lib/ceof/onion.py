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

        if args.message:
            peer = ceof.Peer.from_disk(config.peer_dir, args.name)
            route = ceof.TransportProtocol.route_to(config.peer_dir, peer, ceof.EOF_L_ROUTERS)
            chain = ceof.TransportProtocol.chained_pkg(route, peer, args.message)

            onion = cls(config.gpg_config_dir)

            onion_chain = onion.chain(chain)
            print(onion_chain)

        if args.send:
            first = chain[-1]
            address = first['address']
            print("Sending generated message via %s to %s" % (str(chain), str(address)))

            import socket
            import urllib.parse
            url = urllib.parse.urlparse(address)
            host, port = url.netloc.split(":")
            host = "127.0.0.1"
            try:
                mysocket = socket.create_connection((host, port))
            except socket.error as e:
                raise OnionError("Cannot connect to %s: %s" % ((host, port), e))

            data = onion_chain.encode('utf-8')
            mysocket.sendall(data)

    # FIXME: do not encrypt last round, because we send to this peer!
    def chain(self, chained_pkg):
        """Create onion chain"""

        log.debug(chained_pkg)
        onion_chain = ""
        lastaddr=""
        for pkg in chained_pkg:
            log.debug("Chain pkg:" + str(pkg))
            onion_chain = self.pkg(pkg, onion_chain, lastaddr)
            lastaddr = pkg['address']
            log.debug("Returned Chain: %s" % str(onion_chain))

        return onion_chain

    def pkg(self, pkg, onion, lastaddr):
        """Create an onion"""

        cmd = pkg['cmd']

        # empty core of the onion
        eofmsg = ceof.EOFMsg(cmd=cmd)
        log.debug(repr(str(eofmsg)))

        # Nothing added when dropping the package
        if cmd == ceof.EOF_CMD_ONION_DROP:
            pass

        elif cmd == ceof.EOF_CMD_ONION_FORWARD:
            eofmsg.address = lastaddr

        elif cmd == ceof.EOF_CMD_ONION_MSG_DROP:
            eofmsg.msgtext = pkg['message']
            
        elif cmd == ceof.EOF_CMD_ONION_MSG_FORWARD:
            eofmsg.msgtext = pkg['message']
            eofmsg.address = lastaddr

        return str(self.crypto.encrypt(str(eofmsg) + onion, pkg['peer'].fingerprint))
