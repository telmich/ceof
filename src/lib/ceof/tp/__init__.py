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

class TransportProtocolError(ceof.Error):
    pass

class TransportProtocol(object):
    """Common transport helper"""

    def __init__(self):
        pass

    @classmethod
    def commandline(cls, args, config):
        if (args.route_to or args.chain_to) and not args.name:
            raise TransportProtocolError("Requiring peer name for routing/chaining")

        if args.list:
            for protocol in cls.list_protocols():
                print(protocol)
        elif args.route_to:
            peer = ceof.Peer.from_disk(config.peer_dir, args.name)
            route = cls.route_to(config.peer_dir, peer, ceof.EOF_L_ROUTERS)
            print(route)
        elif args.chain_to:
            peer = ceof.Peer.from_disk(config.peer_dir, args.name)
            route = cls.route_to(config.peer_dir, peer, ceof.EOF_L_ROUTERS)
            chain = cls.chained_pkg(route, peer, "test")
            print(chain)

    @staticmethod
    def list_protocols():
        protocols = []
        filename = "__init__.py"
        base_dir = os.path.dirname(os.path.realpath(__file__))

        for possible_protocol in os.listdir(base_dir):
            mod_path = os.path.join(base_dir, possible_protocol, filename)

            if os.path.isfile(mod_path):
                protocols.append(possible_protocol)

        return protocols
     
    @classmethod
    def verify_scheme(cls, address):
        """Verify given address if the scheme (=protocol) is available"""
        protocols = cls.list_protocols()

        match = re.match("(.*?)://", address)
        if not match:
            return False

        protocol = match.group(1)

        return protocol in protocols

    @staticmethod
    def route_to(peer_dir, peer, num_peers):
        """Get route to a peer"""
        peers = ceof.Peer.list_random_peers(peer_dir, num_peers, notthispeer=peer)

        peer_index = random.randrange(len(peers))
        peers.insert(peer_index, peer)

        return peers

    @staticmethod
    def chained_pkg(route, peer, message):
        """Create chained packet"""

        # First peer that receives is the last one that last decrypts
        first_peer = True
        msg=""
        pkg = []
        for router in route:
            router_pkg = {}
            router_pkg['peer'] = router
            router_pkg['address'] = peer.random_address()

            if router == peer:
                router_pkg['message'] = message
                if first_peer:
                    router_pkg['cmd'] = ceof.EOF_CMD_ONION_MSG_DROP
                    first_peer = False
                else:
                    router_pkg['cmd'] = ceof.EOF_CMD_ONION_MSG_FORWARD
            else:
                payload = ""
                if first_peer:
                    router_pkg['cmd'] = ceof.EOF_CMD_ONION_DROP
                    first_peer = False
                else:
                    router_pkg['cmd'] = ceof.EOF_CMD_ONION_FORWARD

            pkg.append(router_pkg)
            # pkg.append("%s/%s/%s" % (router.name, address, cmd))

        return pkg

################################################################################
    @staticmethod
    def send(text, destination):
        """Send packet from queue"""

        route = self.route_to(destination)

        self.onion()

    def _run(self):
        """Main loop"""

        while not self.doexit:
            # Try to get message, send noise otherwise
            try:
                text, destination = self.message_queue.get(False)
                message = True
            except queue.Empty:
                message = False

            if not message:
                try:
                    text = self.noise_queue.get()
                except queue.Empty:
                    raise NoiseQueueEmptyError

                destination = self.random_recipient()

            self.send(text, destination)