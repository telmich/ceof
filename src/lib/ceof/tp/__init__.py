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
import urllib.parse

log = logging.getLogger(__name__)

class TransportProtocolError(ceof.Error):
    pass

class NoSuchTransportProtocolError(ceof.Error):
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
            route = cls.route_to(config.peer_dir, peer, ceof.EOF_L_ADDITIONAL_PEERS)
            print(route)
        elif args.chain_to:
            peer = ceof.Peer.from_disk(config.peer_dir, args.name)
            route = cls.route_to(config.peer_dir, peer, ceof.EOF_L_ADDITIONAL_PEERS)
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
    def get_module(cls, address):
        """Get module handling address"""

        if not cls.verify_scheme(address):
            handler = None
        else:
            url = urllib.parse.urlparse(address)
            modname = __name__ + url.scheme
            print(modname)
            handler = modname

        return handler


    @classmethod
    def verify_scheme(cls, address):
        """Verify given address if the scheme (=protocol) is available"""
        protocols = cls.list_protocols()

        url = urllib.parse.urlparse(address)

        if not url.scheme in protocols:
            raise NoSuchTransportProtocolError

    @staticmethod
    def route_to(peer_dir, peer, num_peers):
        """Get route to a peer"""

        # Get some random peers, not the target included
        peers = ceof.Peer.list_random_peers(peer_dir, num_peers, notthispeer=peer)

        # Insert the target at a random position (including last one!)
        peer_index = random.randrange(len(peers) + 1)
        peers.insert(peer_index, peer)

        return peers
